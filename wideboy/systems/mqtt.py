import json
import logging
from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient, MQTTMessage
from typing import Any, Dict, List
from ..consts import EventTypes
from ..entities import AppState, MQTTService
from ..homeassistant import HomeAssistantEntity


logger = logging.getLogger(__name__)


class SysMQTT(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.app_state = None
        self.client = MQTTClient()

    def start(self) -> None:
        logger.info("MQTT system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))
        if not self.app_state:
            raise Exception("AppState not found")
        self.client.username_pw_set(
            self.app_state.config.mqtt.user, self.app_state.config.mqtt.password
        )
        self.client.on_message = self._on_message
        self.client.connect(
            self.app_state.config.mqtt.host,
            self.app_state.config.mqtt.port,
            self.app_state.config.mqtt.keepalive,
        )
        listeners = []
        if self.app_state.config.mqtt.log_messages:
            listeners.append(self.debug_listener)
        self.entities.add(MQTTService(client=self.client, listeners=listeners))

    def update(self) -> None:
        self.client.loop(timeout=0.005)

    def debug_listener(self, topic: str, payload: str, client: MQTTClient) -> None:
        logger.debug(f"sys.mqtt.message: topic: {topic}, payload: {payload}")

    def _on_message(
        self, client: MQTTClient, userdata: Any, message: MQTTMessage
    ) -> None:
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        for listener in mqtt_service.listeners:
            listener(topic, payload, client)


class SysHomeAssistant(System):
    topic_prefix_default: str
    topic_prefix_statestream: str
    topic_prefix_app: str
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
        self.mqtt.listeners.append(self._on_mqtt_message)
        config = next(self.entities.get_by_class(AppState)).config
        self.topic_prefix_default = config.mqtt.topic_prefix.homeassistant.default
        self.topic_prefix_statestream = (
            config.mqtt.topic_prefix.homeassistant.statestream
        )
        self.app_id = config.general.device_id
        self.topic_prefix_app = config.mqtt.topic_prefix.app
        self.mqtt.client.subscribe(f"{self.topic_prefix_app}/#")
        self.mqtt.client.subscribe(f"{self.topic_prefix_statestream}/#")
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
                    entity.config["state_topic"], entity.to_hass_state(), qos=1
                )

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
        entity.callback(client, app_state, entity.config["state_topic"], payload)
