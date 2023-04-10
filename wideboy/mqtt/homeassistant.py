import json
import logging
import pygame
from typing import Optional
from homeassistant_api import Client

from wideboy.constants import (
    AppMetadata,
    EVENT_MQTT_MESSAGE_SEND,
)
from wideboy.config import DEVICE_ID, settings


logger = logging.getLogger("mqtt.homeassistant")


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


HASS = setup_hass()

print(
    HASS.request(
        "calendars/calendar.wideboy?start=2023-04-08T10:00:00.000Z&end=2024-12-25T10:00:00.000Z"
    )
)


def advertise_entity(
    name: str,
    device_class: str,
    options: Optional[dict] = None,
    initial_state: Optional[dict] = None,
) -> None:
    if options is None:
        options = dict()
    entity_id = build_entity_id(name)
    config_topic = f"{HASS_TOPIC_PREFIX}/{device_class}/{entity_id}/config"
    command_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/set"
    state_topic = f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{name}/state"
    config = dict(
        name=name,
        object_id=entity_id,
        unique_id=entity_id,
        device=build_device_info(),
    )
    if device_class in ["sensor", "switch", "light"]:
        config["device_class"] = device_class
        config["state_topic"] = state_topic
        config["schema"] = "json"
    if device_class in ["switch", "light", "button", "text"]:
        config["command_topic"] = command_topic
    if device_class in ["button"]:
        config["entity_category"] = "config"
    config.update(options)
    if initial_state is None:
        initial_state = dict()
    logger.debug(f"hass:mqtt:config name={name} config={config}")
    pygame.event.post(
        pygame.event.Event(
            EVENT_MQTT_MESSAGE_SEND,
            topic=config_topic,
            payload=config,
            auto_prefix=False,
        )
    )
    if device_class in ["sensor", "switch", "light"]:
        pygame.event.post(
            pygame.event.Event(
                EVENT_MQTT_MESSAGE_SEND,
                topic=state_topic,
                payload=initial_state,
                auto_prefix=False,
            )
        )


def update_entity(topic: str, payload: dict):
    pygame.event.post(
        pygame.event.Event(
            EVENT_MQTT_MESSAGE_SEND,
            topic=topic,
            payload=payload,
        ),
    )


def update_sensors(clock: pygame.time.Clock, every_tick: int = 5000):
    if pygame.time.get_ticks() % every_tick == 0:
        update_entity("fps/state", dict(value=clock.get_fps()))


def hass_bool(value: bool) -> str:
    return "ON" if value else "OFF"


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
