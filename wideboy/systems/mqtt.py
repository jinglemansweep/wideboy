import json
import logging
import time
from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient, MQTTMessage
from typing import Any, Dict, List
from ..consts import EventTypes
from ..entities import AppState, MQTTService
from ..homeassistant import HomeAssistantEntity


logger = logging.getLogger(__name__)

MQTT_RECONNECT_WAIT = 5  # secs


class SysMQTT(System):
    def __init__(self, entities: EntityManager, auto_connect=False) -> None:
        self.entities = entities
        self.auto_connect = auto_connect
        self.app_state = None
        self.client = MQTTClient()
        self.mqtt_connected = False

    def start(self) -> None:
        logger.info("MQTT system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))
        if not self.app_state:
            raise Exception("AppState not found")
        on_connect_listeners = [self.debug_connect_listener]
        on_disconnect_listeners = [self.debug_disconnect_listener]
        on_message_listeners = []
        self.client.username_pw_set(
            self.app_state.config.mqtt.user, self.app_state.config.mqtt.password
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        if self.app_state.config.mqtt.log_messages:
            on_message_listeners.append(self.debug_message_listener)
        self.entities.add(
            MQTTService(
                client=self.client,
                connect_callback=self.connect,
                on_connect_listeners=on_connect_listeners,
                on_disconnect_listeners=on_disconnect_listeners,
                on_message_listeners=on_message_listeners,
            )
        )
        if self.auto_connect:
            self.connect()

    def update(self) -> None:
        try:
            self.client.loop(timeout=0.01)
        except Exception as e:
            logger.error(f"sys.mqtt.update: exception={e}")
        if not self.mqtt_connected:
            logger.warning(
                f"sys.mqtt.reconnect: connected={self.mqtt_connected} retry={MQTT_RECONNECT_WAIT}s"
            )
            time.sleep(MQTT_RECONNECT_WAIT)
            try:
                self.client.reconnect()
            except Exception as e:
                logger.error(f"sys.mqtt.reconnect: exception={e}")

    def debug_connect_listener(
        self, client: MQTTClient, userdata: Any, flags: Any, rc: int
    ) -> None:
        logger.debug(f"sys.mqtt.connect: connected={self.mqtt_connected}")

    def debug_disconnect_listener(
        self, client: MQTTClient, userdata: Any, rc: int
    ) -> None:
        logger.debug(f"sys.mqtt.disconnect: connected={self.mqtt_connected}")

    def debug_message_listener(
        self, topic: str, payload: str, client: MQTTClient
    ) -> None:
        logger.debug(f"sys.mqtt.message: topic: {topic}, payload: {payload}")

    def _on_connect(self, client: MQTTClient, userdata: Any, flags: Any, rc: int):
        self.mqtt_connected = rc == 0
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        for listener in mqtt_service.on_connect_listeners:
            listener(client, userdata, flags, rc)

    def _on_disconnect(self, client: MQTTClient, userdata: Any, rc: int):
        self.mqtt_connected = rc == 0
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        for listener in mqtt_service.on_disconnect_listeners:
            listener(client, userdata, rc)

    def _on_message(
        self, client: MQTTClient, userdata: Any, message: MQTTMessage
    ) -> None:
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        for listener in mqtt_service.on_message_listeners:
            listener(topic, payload, client)

    def connect(self):
        self.client.connect(
            self.app_state.config.mqtt.host,
            self.app_state.config.mqtt.port,
            self.app_state.config.mqtt.keepalive,
        )
        self.client.loop()


class SysHomeAssistant(System):
    topic_prefix_default: str
    topic_prefix_statestream: str
    topic_prefix_app: str
    subscriptions: List[str] = []
    commands: Dict[str, HomeAssistantEntity] = {}

    def __init__(
        self, entities: EntityManager, hass_entities: List[HomeAssistantEntity]
    ) -> None:
        self.entities = entities
        self.hass_entities = hass_entities
        self.mqtt = None

    def start(self) -> None:
        logger.info("HomeAssistant system starting...")
        self.mqtt = next(self.entities.get_by_class(MQTTService))
        if not self.mqtt:
            raise Exception("MQTTService not found")
        self.mqtt.on_connect_listeners.append(self._on_mqtt_connect)
        self.mqtt.on_message_listeners.append(self._on_mqtt_message)
        config = next(self.entities.get_by_class(AppState)).config
        self.topic_prefix_default = config.mqtt.topic_prefix.homeassistant.default
        self.topic_prefix_statestream = (
            config.mqtt.topic_prefix.homeassistant.statestream
        )
        self.app_id = config.general.device_id
        self.topic_prefix_app = config.mqtt.topic_prefix.app
        self.subscriptions = [
            f"{self.topic_prefix_app}/#",
            f"{self.topic_prefix_statestream}/#",
        ]
        self.mqtt.connect_callback()
        self._advertise_entities()

    def _advertise_entities(self):
        for EntityCls in self.hass_entities:
            entity = EntityCls(self.app_id, self.topic_prefix_app)
            logger.debug(
                f"sys.mqtt.advertise: topic={entity.topic_config} config={entity.config}"
            )
            self.mqtt.client.publish(
                entity.topic_config, json.dumps(entity.config), qos=1, retain=True
            )
            if "command_topic" in entity.config:
                self.commands[entity.config["command_topic"]] = entity
            if entity.initial_state:
                logger.debug(
                    f"sys.mqtt.state: entity={entity.name} state={entity.to_hass_state()}"
                )
                self.mqtt.client.publish(
                    entity.config["state_topic"],
                    entity.to_hass_state(),
                    qos=1,
                    retain=True,
                )

    def _on_mqtt_connect(self, client: MQTTClient, userdata: Any, flags: Any, rc: int):
        connected = rc == 0
        logger.debug(f"sys.hass.connect: connected={connected}")
        for topic in self.subscriptions:
            logger.debug(f"sys.hass.mqtt.subscribe: topic={topic}")
            client.subscribe(topic)

    def _on_mqtt_message(self, topic: str, payload: str, client: MQTTClient) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        if topic.startswith(f"{self.topic_prefix_statestream}/"):
            self._handle_statestream_message(topic, payload, app_state)
        elif topic in self.commands:
            self._handle_command_message(topic, payload, app_state, client)

    def _handle_statestream_message(
        self, topic: str, payload: str, app_state: AppState
    ) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        if topic.startswith(f"{self.topic_prefix_statestream}/"):
            parts = topic[len(self.topic_prefix_statestream) :].split("/")
            device_class, entity_id, attr = parts[1], parts[-2], parts[-1]
            entity_id_full = f"{device_class}.{entity_id}"
            app_state.events.append(
                (
                    EventTypes.EVENT_HASS_ENTITY_UPDATE,
                    dict(entity_id=entity_id_full, attribute=attr, payload=payload),
                )
            )
            if entity_id_full not in app_state.hass_state:
                app_state.hass_state[entity_id_full] = dict()
            app_state.hass_state[entity_id_full][attr] = payload

    def _handle_command_message(
        self, topic: str, payload: str, app_state: AppState, client: MQTTClient
    ) -> None:
        logger.debug(f"sys.hass.command: topic: {topic}, payload: {payload}")
        entity = self.commands[topic]
        entity.callback(
            client, app_state, entity.config.get("state_topic", None), payload
        )
