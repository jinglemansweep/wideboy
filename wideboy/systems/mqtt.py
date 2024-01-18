import json
import logging
from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient
from pygame.event import Event, post as post_event
from typing import Any, Dict
from ..consts import EVENT_HASS_ENTITY_UPDATE
from ..entities import AppState, MQTTService
from ..homeassistant import SwitchEntity

logger = logging.getLogger(__name__)


def switch_power_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
):
    state.power = payload == "ON"
    client.publish(
        entity_config["state_topic"],
        "ON" if state.power else "OFF",
        qos=1,
    )


class SysMQTT(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.app_state = None
        self.client = MQTTClient()

    def start(self):
        logger.info("MQTT system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))
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

    def update(self):
        self.client.loop(timeout=0.001)

    def debug_listener(self, topic: str, payload: str, client: MQTTClient) -> None:
        logger.debug(f"sys.mqtt.message: topic: {topic}, payload: {payload}")

    def _on_message(self, client: MQTTClient, userdata: Any, message: Any):
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        for listener in mqtt_service.listeners:
            listener(topic, payload, client)


class SysHomeAssistant(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.mqtt = None

    def start(self):
        logger.info("HomeAssistant system starting...")
        self.mqtt = next(self.entities.get_by_class(MQTTService))
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
        hass_entities = [
            SwitchEntity(
                "power",
                self.app_id,
                self.topic_prefix_app,
                initial_state="OFF",
                callback=switch_power_callback,
            ),
        ]
        self.command_topics = {}
        for entity in hass_entities:
            config = entity.configure()
            topic = entity.configure_topic()
            self.mqtt.client.publish(
                topic,
                json.dumps(config),
                qos=1,
            )
            if "command_topic" in config:
                self.command_topics[config["command_topic"]] = entity
            if entity.initial_state:
                self.mqtt.client.publish(
                    config["state_topic"],
                    entity.to_hass_state(),
                    qos=1,
                )

    def _on_mqtt_message(self, topic, payload, client):
        app_state = next(self.entities.get_by_class(AppState))
        # STATESTREAM
        if topic.startswith(f"{self.topic_prefix_statestream}/"):
            parts = topic[len(self.topic_prefix_statestream) :].split("/")
            device_class, entity_id, attr = parts[1], parts[-2], parts[-1]
            entity_id_full = f"{device_class}.{entity_id}"
            post_event(
                Event(
                    EVENT_HASS_ENTITY_UPDATE,
                    dict(entity_id=entity_id_full, attribute=attr, payload=payload),
                )
            )
            if entity_id_full not in app_state.hass_state:
                app_state.hass_state[entity_id_full] = dict()
            app_state.hass_state[entity_id_full][attr] = payload
        # MQTT CONTROLS
        elif topic in self.command_topics:
            logger.debug(f"sys.hass.command: topic: {topic}, payload: {payload}")
            entity = self.command_topics[topic]
            entity.callback(client, entity.config, app_state, payload)
