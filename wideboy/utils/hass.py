import json
import logging
import pygame
from paho.mqtt.client import Client as MQTTClient
from typing import Any, Optional
from homeassistant_api import Client

from wideboy import _APP_NAME, _APP_VERSION, _APP_AUTHOR
from wideboy.config import HASS_URL, HASS_API_TOKEN, MQTT_TOPIC_PREFIX
from wideboy.utils.device import DEVICE_ID
from wideboy.utils.mqtt import MQTT

logger = logging.getLogger(__name__)

EVENT_HASS_COMMAND = pygame.USEREVENT + 31

HASS_TOPIC_PREFIX = "homeassistant"

MODEL_NAME = _APP_NAME
MANUFACTURER_NAME = _APP_AUTHOR


def setup_hass() -> Client:
    api_url = f"{HASS_URL}/api"
    hass = Client(api_url, HASS_API_TOKEN)
    return hass


def advertise_entity(
    name: str,
    device_class: str,
    options: Optional[dict] = None,
) -> None:
    if options is None:
        options = dict()
    entity_id = build_entity_id(name)
    config_topic = f"{HASS_TOPIC_PREFIX}/{device_class}/{entity_id}/config"
    command_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/set"
    state_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/state"
    config = dict(
        name=name,
        device_class=device_class,
        object_id=entity_id,
        unique_id=entity_id,
        command_topic=command_topic,
        state_topic=state_topic,
        device=build_device_info(),
        schema="json",
    )
    config.update(options)
    MQTT.publish(config_topic, config, auto_prefix=False)


def build_device_info() -> dict:
    full_device_id = f"{MODEL_NAME}_{DEVICE_ID}"
    return dict(
        identifiers=[full_device_id],
        name=full_device_id,
        model=MODEL_NAME,
        manufacturer=MANUFACTURER_NAME,
        sw_version=_APP_VERSION,
    )


def build_entity_id(name: str) -> str:
    return f"{_APP_NAME}_{DEVICE_ID}_{name}"


def build_entity_topic_prefix(device_class: str, full_name) -> str:
    return f"{MQTT_TOPIC_PREFIX}/{device_class}/{full_name}"
