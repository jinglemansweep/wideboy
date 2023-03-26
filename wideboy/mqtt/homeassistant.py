import json
import logging
import pygame
from paho.mqtt.client import Client as MQTTClient
from typing import Any, Optional, Union
from homeassistant_api import Client

from wideboy.constants import AppMetadata
from wideboy.config import settings
from wideboy.mqtt import MQTT
from wideboy.state import DEVICE_ID


logger = logging.getLogger(__name__)

EVENT_HASS_COMMAND = pygame.USEREVENT + 31

MQTT_TOPIC_PREFIX = settings.mqtt.topic_prefix
HASS_URL = settings.homeassistant.url
HASS_API_TOKEN = settings.homeassistant.api_token
HASS_TOPIC_PREFIX = "homeassistant"


MODEL_NAME = AppMetadata.TITLE
MANUFACTURER_NAME = AppMetadata.AUTHOR
SW_VERSION = AppMetadata.VERSION


def setup_hass() -> Client:
    api_url = f"{HASS_URL}/api"
    hass = Client(api_url, HASS_API_TOKEN)
    return hass


class HASSEntity:
    def __init__(
        self,
        name: str,
        device_class: str = "switch",
        options: Optional[dict] = None,
        initial_state: Optional[dict] = None,
    ):
        self.name = name
        self.device_class = device_class
        self.entity_id = build_entity_id(name)
        self.config_topic = (
            f"{HASS_TOPIC_PREFIX}/{device_class}/{self.entity_id}/config"
        )
        self.command_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/set"
        self.state_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/state"
        self.config = dict(
            name=name,
            device_class=device_class,
            object_id=self.entity_id,
            unique_id=self.entity_id,
            command_topic=self.command_topic,
            state_topic=self.state_topic,
            device=build_device_info(),
            schema="json",
        )
        if options:
            self.config.update(options)
        self.state = initial_state or dict()
        MQTT.publish(self.config_topic, self.config, auto_prefix=False)
        self.update(self.state)

    def update(self, new_state: Optional[Union[dict, str]] = None):
        if new_state:
            if isinstance(new_state, str):
                self.state.update(dict(state=new_state))
            else:
                self.state.update(new_state)
            MQTT.publish(
                self.state_topic,
                self.state,
                auto_prefix=False,
            )


def build_device_info() -> dict:
    full_device_id = f"{MODEL_NAME}_{DEVICE_ID}"
    return dict(
        identifiers=[full_device_id],
        name=full_device_id,
        model=MODEL_NAME,
        manufacturer=MANUFACTURER_NAME,
        sw_version=SW_VERSION,
    )


def build_entity_id(name: str) -> str:
    return f"{AppMetadata.NAME}_{DEVICE_ID}_{name}"


def build_entity_topic_prefix(device_class: str, full_name) -> str:
    return f"{MQTT_TOPIC_PREFIX}/{device_class}/{full_name}"
