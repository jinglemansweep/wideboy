import json
import logging
import pygame
from dynaconf import Dynaconf
from pygame import Event
from typing import Optional, TYPE_CHECKING
from homeassistant_api import Client

from wideboy.config import settings
from wideboy.constants import (
    AppMetadata,
)
from wideboy.homeassistant.mqtt import MQTTClient

logger = logging.getLogger("homeassistant")


class HASSEntity:
    def __init__(
        self,
        device_class: str,
        name: str,
        options: Optional[dict] = None,
        initial_state: Optional[dict] = None,
    ):
        self.device_class = device_class
        self.name = name
        self.options = options
        self.initial_state = initial_state


class HASSManager:
    def __init__(self, mqtt: MQTTClient, device_id: str):
        self.mqtt = mqtt
        self.device_id = device_id
        self.client = Client(
            f"{settings.homeassistant.url}/api",
            settings.homeassistant.api_token,
            cache_session=False,
        )

    def advertise_entities(self, entities: list[HASSEntity]) -> None:
        for entity in entities:
            self.advertise_entity(
                entity.name, entity.device_class, entity.options, entity.initial_state
            )

    def advertise_entity(
        self,
        name: str,
        device_class: str,
        options: Optional[dict] = None,
        initial_state: Optional[dict] = None,
    ) -> None:
        if options is None:
            options = dict()
        entity_id = self.build_entity_id(name)
        config_topic = (
            f"{settings.homeassistant.topic_prefix}/{device_class}/{entity_id}/config"
        )
        command_topic = f"{settings.mqtt.topic_prefix}/{self.device_id}/{name}/set"
        state_topic = f"{settings.mqtt.topic_prefix}/{self.device_id}/{name}/state"
        config = dict(
            name=name,
            object_id=entity_id,
            unique_id=entity_id,
            device=self.build_device_info(),
        )
        if device_class in ["sensor", "switch", "light", "select"]:
            config["device_class"] = device_class
            config["state_topic"] = state_topic
            config["schema"] = "json"
        if device_class in ["switch", "light", "button", "text", "select"]:
            config["command_topic"] = command_topic
        if device_class in ["button"]:
            config["entity_category"] = "config"
        config.update(options)
        if initial_state is None:
            initial_state = dict()
        logger.debug(f"hass:mqtt:config name={name} config={config}")
        self.mqtt.publish(config_topic, config)
        if device_class in ["sensor", "switch", "light", "select"]:
            self.mqtt.publish(state_topic, initial_state)

    def build_device_info(self) -> dict:
        full_device_id = f"{_get_app_id()}_{self.device_id}"
        return dict(
            identifiers=[full_device_id],
            name=full_device_id,
            model=AppMetadata.TITLE,
            manufacturer=AppMetadata.AUTHOR,
            sw_version=AppMetadata.VERSION,
        )

    def build_entity_id(self, name: str) -> str:
        return f"{_get_app_id()}_{self.device_id}_{name}"


def _get_app_id():
    return AppMetadata.NAME.lower()
