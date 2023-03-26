import json
import logging
import pygame
from typing import Optional
from homeassistant_api import Client

from wideboy.constants import AppMetadata
from wideboy.config import settings
from wideboy.mqtt import MQTT, EVENT_MQTT_MESSAGE
from wideboy.state import DEVICE_ID
from wideboy.utils.pygame import EVENT_MASTER_POWER, EVENT_MASTER_BRIGHTNESS

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
        device_class=device_class,
        object_id=entity_id,
        unique_id=entity_id,
        command_topic=command_topic,
        state_topic=state_topic,
        device=build_device_info(),
        schema="json",
    )
    config.update(options)
    if initial_state is None:
        initial_state = dict()
    MQTT.publish(config_topic, config, auto_prefix=False)
    MQTT.publish(state_topic, initial_state, auto_prefix=False)


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


def process_hass_mqtt_events(events: list[pygame.event.Event]):
    for event in events:
        if event.type == EVENT_MQTT_MESSAGE:
            if event.topic.endswith("master/set"):
                try:
                    payload = json.loads(event.payload)
                    logger.debug(f"master/set payload={payload}")
                except Exception as e:
                    logger.warn("hass:mqtt:event error={e}")
                pygame.event.post(
                    pygame.event.Event(
                        EVENT_MASTER_POWER, value=payload["state"] == "ON"
                    )
                )
                pygame.event.post(
                    pygame.event.Event(
                        EVENT_MASTER_BRIGHTNESS, value=payload["brightness"]
                    )
                )
            if event.topic.endswith("select_scene/set"):
                pass


advertise_entity(
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
    dict(state="ON", brightness=128),
)
