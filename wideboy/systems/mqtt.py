import json
import logging
from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient, MQTTMessage
from pygame.event import Event, post as post_event
from typing import Any, Dict
from ..consts import EVENT_HASS_ENTITY_UPDATE
from ..entities import AppState, MQTTService
from ..homeassistant import (
    ButtonEntity,
    LightEntity,
    NumberEntity,
    SelectEntity,
    SwitchEntity,
    TextEntity,
    strip_quotes,
    to_hass_bool,
)

logger = logging.getLogger(__name__)


def button_state_log_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    logger.debug("sys.hass.entities.button.state_log: press")
    logger.info(f"app_state: {state}")


def switch_power_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    state.power = payload == "ON"
    logger.debug(f"sys.hass.entities.power: state={state.power}")
    client.publish(
        entity_config["state_topic"],
        to_hass_bool(state.power),
        qos=1,
    )


def light_light_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    payload_dict = json.loads(payload)
    state.light_state = payload_dict["state"] == "ON"
    if "brightness" in payload_dict:
        state.light_brightness = int(payload_dict["brightness"])
    logger.debug(
        f"sys.hass.entities.lighttest: topic={entity_config['state_topic']} state={state.light_state} brightness={state.light_brightness}"
    )
    client.publish(
        entity_config["state_topic"],
        json.dumps(
            {
                "state": to_hass_bool(state.light_state),
                "brightness": state.light_brightness,
            }
        ),
        qos=1,
    )


def number_number_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    state.number_state = float(payload)
    logger.debug(f"sys.hass.entities.number: state={state.number_state}")
    client.publish(
        entity_config["state_topic"],
        state.number_state,
        qos=1,
    )


def select_select_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    state.select_state = payload
    logger.debug(f"sys.hass.entities.select: state={state.select_state}")
    client.publish(
        entity_config["state_topic"],
        state.select_state,
        qos=1,
    )


def text_text_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    state.text_state = payload
    logger.debug(f"sys.hass.entities.text: state={state.text_state}")
    client.publish(
        entity_config["state_topic"],
        strip_quotes(state.text_state),
        qos=1,
    )


def button_button_callback(
    client: MQTTClient, entity_config: Dict[str, Any], state: AppState, payload: str
) -> None:
    state.button_flag = not state.button_flag
    logger.debug(f"sys.hass.entities.button: state={state.button_flag}")


ENTITIES = [
    {"cls": ButtonEntity, "name": "state_log", "callback": button_state_log_callback},
    {
        "cls": SwitchEntity,
        "name": "power",
        "callback": switch_power_callback,
        "initial_state": "OFF",
    },
    {
        "cls": LightEntity,
        "name": "light",
        "options": {
            "brightness": True,
            "supported_color_mode": ["brightness"],
        },
        "callback": light_light_callback,
        "initial_state": {"state": "ON", "brightness": 255},
    },
    {
        "cls": NumberEntity,
        "name": "number",
        "options": {
            "device_class": "duration",
            "step": 0.1,
            "min": 0,
            "max": 10,
        },
        "callback": number_number_callback,
        "initial_state": 5.0,
    },
    {
        "cls": SelectEntity,
        "name": "select",
        "options": {"options": ["opt1", "opt2", "opt3"]},
        "callback": select_select_callback,
        "initial_state": "opt2",
    },
    {
        "cls": TextEntity,
        "name": "text",
        "callback": text_text_callback,
        "initial_state": "Hello",
    },
    {"cls": ButtonEntity, "name": "test", "callback": button_button_callback},
]


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
        self.client.loop(timeout=0.001)

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

    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
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
        self.command_topics = {}
        for entity_config in ENTITIES:
            EntityCls = entity_config.get("cls")
            entity = EntityCls(
                entity_config.get("name"),
                self.app_id,
                self.topic_prefix_app,
                initial_state=entity_config.get("initial_state", {}),
                options=entity_config.get("options", {}),
                callback=entity_config.get("callback"),
            )
            config = entity.configure()
            topic = entity.configure_topic()
            logger.debug(f"sys.mqtt.advertise: topic={topic} config={config}")
            self.mqtt.client.publish(topic, json.dumps(config), qos=1, retain=True)
            if "command_topic" in config:
                self.command_topics[config["command_topic"]] = entity
            if entity.initial_state:
                self.mqtt.client.publish(
                    config["state_topic"],
                    entity.to_hass_state(),
                    qos=1,
                    retain=True,
                )

    def _on_mqtt_message(self, topic: str, payload: str, client: MQTTClient) -> None:
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
