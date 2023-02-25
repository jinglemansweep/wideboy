import json
import logging
import pygame
from paho.mqtt.client import Client as MQTTClient
from typing import Optional
from homeassistant_api import Client

from wideboy import _APP_NAME, _APP_VERSION, _APP_AUTHOR
from wideboy.config import HASS_URL, HASS_API_TOKEN
from wideboy.utils.helpers import get_device_id

EVENT_HASS_TEST = pygame.USEREVENT + 31

logger = logging.getLogger(__name__)

DISCOVERY_PREFIX = "homeassistant"
DEVICE_ID = get_device_id()
MODEL_NAME = _APP_NAME
MANUFACTURER_NAME = _APP_AUTHOR


def setup_hass() -> Client:
    api_url = f"{HASS_URL}/api"
    hass = Client(api_url, HASS_API_TOKEN)
    return hass


class MQTTEntity:
    def __init__(
        self,
        mqtt_client: MQTTClient,
        name: str,
        device_class: str,
        options: Optional[dict] = None,
        default_state: Optional[dict] = None,
    ) -> None:
        self.mqtt_client = mqtt_client
        self.name = name
        self.device_class = device_class
        if options is None:
            options = dict()
        self.options = options
        if default_state is None:
            default_state = dict()
        self.state = default_state
        self.entity_id = build_entity_name(name)
        self.topic_prefix = build_entity_topic_prefix(device_class, self.entity_id)
        self.configure()

    def advertise(self) -> None:
        self._publish("config", self.config)

    def subscribe(self) -> None:
        self.mqtt_client.subscribe(f"{self.topic_prefix}/set", 1)

    def update(self, new_state: dict = None) -> None:
        if new_state is not None:
            self.state.update(new_state)
        self._publish("state", self.state)

    def configure(self) -> None:
        self.config = self._build_configuration()

    def _publish(
        self, topic: str, payload: dict, retain: bool = True, qos: int = 1
    ) -> None:
        full_topic = f"{self.topic_prefix}/{topic}"
        json_payload = json.dumps(payload)
        logger.debug(f"hass:mqtt:publish topic={full_topic} payload={json_payload}")
        self.mqtt_client.publish(full_topic, json_payload, retain=retain, qos=qos)

    def _build_configuration(self) -> dict:
        auto_config = dict(
            name=self.name,
            device_class=self.device_class,
            object_id=self.entity_id,
            unique_id=self.entity_id,
            command_topic=f"{self.topic_prefix}/set",
            state_topic=f"{self.topic_prefix}/state",
            device=build_device_info(),
            schema="json",
        )
        config = auto_config.copy()
        config.update(self.options)
        return config


def build_device_info() -> dict:
    full_device_id = f"{MODEL_NAME}_{DEVICE_ID}"
    return dict(
        identifiers=[full_device_id],
        name=full_device_id,
        model=MODEL_NAME,
        manufacturer=MANUFACTURER_NAME,
        sw_version=_APP_VERSION,
    )


def build_entity_name(name: str) -> str:
    return f"{_APP_NAME}_{DEVICE_ID}_{name}"


def build_entity_topic_prefix(device_class: str, full_name) -> str:
    return f"{DISCOVERY_PREFIX}/{device_class}/{full_name}"


def setup_hass_entities(mqtt_client: MQTTClient) -> list[MQTTEntity]:
    entities = []
    switch_power = MQTTEntity(
        mqtt_client,
        "master_light",
        "light",
        dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
        dict(state="ON", brightness=255),
    )
    switch_power.advertise()
    switch_power.update()
    switch_power.subscribe()
    entities.append(switch_power)
    return entities
