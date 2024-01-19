import json
import logging
from typing import Any, Callable, Dict, Optional

from . import _APP_AUTHOR, _APP_NAME, _APP_TITLE, _APP_VERSION

logger = logging.getLogger(__name__)


def build_entity_prefix(app_id: str):
    return f"{_APP_NAME}_{app_id}".lower()


def build_device_info(app_id: str):
    name = build_entity_prefix(app_id)
    return {
        "identifiers": [name],
        "name": name,
        "model": _APP_TITLE,
        "manufacturer": _APP_AUTHOR,
        "sw_version": _APP_VERSION,
    }


def build_full_entity_id(app_id: str, name: str):
    return f"{build_entity_prefix(app_id)}_{name}".lower()


def to_hass_bool(value: bool) -> str:
    return "ON" if value else "OFF"


def from_hass_bool(value: str) -> bool:
    return value == "ON"


class HomeAssistantEntity:
    device_class: str
    name: str
    topic_prefix: str
    callback: Callable[..., None]
    options: Dict[str, Any] = {}
    options_custom: Dict[str, Any] = {}
    initial_state: Dict[str, Any] = {}
    topic_prefix_homeassistant: str = "homeassistant"
    config: Optional[Dict[str, Any]] = {}

    def __init__(
        self,
        name: str,
        app_id: str,
        topic_prefix: str,
        callback: Callable[..., None],
        options: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        topic_prefix_homeassistant: Optional[str] = None,
    ):
        self.name = name
        self.app_id = app_id
        self.topic_prefix = topic_prefix
        self.callback = callback
        if options:
            self.options_custom = options
        self.initial_state = initial_state or {}
        if topic_prefix_homeassistant:
            self.topic_prefix_homeassistant = topic_prefix_homeassistant

    def to_hass_state(self) -> str:
        return json.dumps(self.initial_state)

    def configure(self):
        options = self.options
        options.update(self.options_custom)
        full_entity_id = build_full_entity_id(self.app_id, self.name)
        topic_template = (
            f"{self.topic_prefix}/{self.app_id}/{self.device_class}/{self.name}"
        )
        if "state_topic" in options:
            options["state_topic"] = options["state_topic"].format(topic_template)
        if "command_topic" in options:
            options["command_topic"] = options["command_topic"].format(topic_template)
        if "json_attributes_topic" in options:
            options["json_attributes_topic"] = options["json_attributes_topic"].format(
                topic_template
            )

        config = {
            "device_class": self.device_class,
            "name": self.name,
            "object_id": full_entity_id,
            "unique_id": full_entity_id,
            "device": build_device_info(self.app_id),
        }
        config.update(options)
        self.config = config
        return config

    def configure_topic(self):
        return f"{self.topic_prefix_homeassistant}/{self.device_class}/{build_full_entity_id(self.app_id, self.name)}/config"


class ButtonEntity(HomeAssistantEntity):
    device_class = "button"
    options = {
        "schema": "json",
        "command_topic": "{}/set",
    }


class LightEntity(HomeAssistantEntity):
    device_class = "light"
    options = {
        "schema": "json",
        "command_topic": "{}/set",
        "state_topic": "{}/state",
        "brightness_command_topic": "{}/brightness/set",
        "brightness_state_topic": "{}/brightness/state",
    }


class SelectEntity(HomeAssistantEntity):
    device_class = "select"
    options = {
        "schema": "json",
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }


class SensorEntity(HomeAssistantEntity):
    device_class = "sensor"
    options = {
        "schema": "json",
        "state_topic": "{}/state",
    }


class SwitchEntity(HomeAssistantEntity):
    device_class = "switch"
    options = {
        "schema": "json",
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }

    def to_hass_state(self) -> str:
        return "ON" if self.initial_state == "ON" else "OFF"


class TextEntity(HomeAssistantEntity):
    device_class = "text"
    options = {
        "schema": "json",
        "command_topic": "{}/set",
    }
