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
    EVENT_HASS_ENTITY_UPDATE,
    EVENT_MQTT_MESSAGE_RECEIVED,
)
from wideboy.homeassistant.mqtt import MQTTClient
from wideboy.utils.helpers import post_event

logger = logging.getLogger("homeassistant")


class HASSEntity:
    def __init__(
        self,
        device_class: str,
        name: str,
        options: Optional[dict] = None,
        initial_state: Optional[dict] = None,
        event_type: Optional[int] = None,
    ):
        self.device_class = device_class
        self.name = name
        self.options = options
        self.initial_state = initial_state
        self.event_type = event_type


class HASSManager:
    def __init__(self, mqtt: MQTTClient, device_id: str):
        self.mqtt = mqtt
        self.device_id = device_id
        self.client = Client(
            f"{settings.homeassistant.url}/api",
            settings.homeassistant.api_token,
            cache_session=False,
        )
        self.entities: dict[str, dict] = dict()

    def handle_event(self, event: Event) -> None:
        if event.type == EVENT_HASS_ENTITY_UPDATE:
            if event.name in self.entities:
                entity = self.entities[event.name]
                logger.debug(
                    f"hass:entity update name={event.name} state={event.state}"
                )
                self.mqtt.publish(entity["config"]["state_topic"], event.state)

        if event.type == EVENT_MQTT_MESSAGE_RECEIVED:
            command_entities = [
                entity
                for entity in self.entities.values()
                if "command_topic" in entity["config"]
            ]
            for entity in command_entities:
                config, event_trigger = entity["config"], entity["event"]
                if event.topic == config["command_topic"]:
                    logger.debug(
                        f"mqtt:command entity={config['name']} topic={event.topic} payload={event.payload}"
                    )
                    if event_trigger:
                        logger.debug(
                            f"mqtt:event entity={config['name']} event={event_trigger} payload={event.payload}"
                        )
                        post_event(event_trigger, payload=event.payload)

    def advertise_entities(self, entities: list[HASSEntity]) -> None:
        for entity in entities:
            self.advertise_entity(entity)

    def advertise_entity(
        self,
        entity: HASSEntity,
    ) -> None:
        options = entity.options or dict()
        entity_id = self.build_entity_id(entity.name)
        config_topic = f"{settings.homeassistant.topic_prefix}/{entity.device_class}/{entity_id}/config"
        command_topic = (
            f"{settings.mqtt.topic_prefix}/{self.device_id}/{entity.name}/set"
        )
        state_topic = (
            f"{settings.mqtt.topic_prefix}/{self.device_id}/{entity.name}/state"
        )
        config = dict(
            name=entity.name,
            object_id=entity_id,
            unique_id=entity_id,
            device=self.build_device_info(),
        )
        if entity.device_class in ["sensor", "switch", "light", "select"]:
            config["device_class"] = entity.device_class
            config["state_topic"] = state_topic
            config["schema"] = "json"
        if entity.device_class in ["switch", "light", "button", "text", "select"]:
            config["command_topic"] = command_topic
        if entity.device_class in ["button"]:
            config["entity_category"] = "config"
        config.update(options)
        self.entities[entity.name] = dict(config=config, event=entity.event_type)
        logger.debug(f"hass:mqtt:config name={entity.name} config={config}")
        self.mqtt.publish(config_topic, config)
        if entity.device_class in ["sensor", "switch", "light", "select"]:
            initial_state = entity.initial_state or dict()
            self.mqtt.publish(state_topic, initial_state)
        logger.debug(f"hass:mqtt:subscribe topic={command_topic}")
        self.mqtt.subscribe(command_topic, 0)

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
