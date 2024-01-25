import json
import logging
from typing import Any, Callable, Dict, Optional
from . import _APP_AUTHOR, _APP_NAME, _APP_TITLE, _APP_VERSION

logger = logging.getLogger(__name__)


def build_entity_prefix(app_id: str) -> str:
    return f"{_APP_NAME}_{app_id}".lower()


def build_device_info(app_id: str) -> Dict[str, Any]:
    name = build_entity_prefix(app_id)
    return {
        "identifiers": [name],
        "name": name,
        "model": _APP_TITLE,
        "manufacturer": _APP_AUTHOR,
        "sw_version": _APP_VERSION,
    }


def to_hass_bool(value: bool) -> str:
    return "ON" if value else "OFF"


def from_hass_bool(value: str) -> bool:
    return value == "ON"


def strip_quotes(value: str) -> str:
    return value.strip('"')


class HomeAssistantEntity:
    device_class: str | None
    name: str
    callback: Callable[..., None]
    topic_prefix_app: str
    topic_prefix_homeassistant: str = "homeassistant"
    description: Optional[str] = None
    entity_options: Dict[str, Any] = {}
    options: Dict[str, Any] = {}
    initial_state: Any = {}

    def __init__(
        self,
        app_id: str,
        topic_prefix_app: str,
        topic_prefix_homeassistant: Optional[str] = None,
    ) -> None:
        self.app_id = app_id
        self.topic_prefix_app = topic_prefix_app
        if topic_prefix_homeassistant:
            self.topic_prefix_homeassistant = topic_prefix_homeassistant

    def to_hass_state(self) -> str:
        return json.dumps(self.initial_state)

    @property
    def config(self) -> Dict[str, Any]:
        opts = self.entity_options.copy()
        opts.update(self.options or {})
        opts.update(
            {
                "name": self.entity_name,
                "object_id": self.entity_id,
                "unique_id": self.entity_id,
                "device": build_device_info(self.app_id),
            }
        )
        if self.device_class is not None:
            opts["device_class"] = self.device_class
        opts.update(self.options or {})
        self._template_topics(opts)
        return opts

    @property
    def entity_id(self) -> str:
        return f"{build_entity_prefix(self.app_id)}_{self.name}".lower()

    @property
    def entity_name(self) -> str:
        return self.description or self.name

    @property
    def topic_prefix(self) -> str:
        return f"{self.topic_prefix_app}/{self.app_id}/{self.topic_device_class}/{self.name}"

    @property
    def topic_config(self) -> str:
        return f"{self.topic_prefix_homeassistant}/{self.topic_device_class}/{self.entity_id}/config"

    @property
    def topic_device_class(self) -> str:
        return self.device_class or "button"

    def _template_topics(self, options: Dict[str, Any]) -> None:
        for key in options:
            if key.endswith("_topic") and isinstance(key, str):
                options[key] = options[key].format(self.topic_prefix)


class ButtonEntity(HomeAssistantEntity):
    device_class = None
    entity_options = {
        "entity_category": "config",
        "command_topic": "{}/set",
        "retain": False,
        "qos": 0,
    }


class LightEntity(HomeAssistantEntity):
    device_class = "light"
    entity_options = {
        "schema": "json",
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }


class NumberEntity(HomeAssistantEntity):
    device_class = "number"
    entity_options = {
        "command_topic": "{}/set",
        "state_topic": "{}/state",
        "step": 1.0,
        "min": 0,
        "max": 100,
    }


class SelectEntity(HomeAssistantEntity):
    device_class = "select"
    entity_options = {
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }

    def to_hass_state(self) -> str:
        return str(self.initial_state)


class SensorEntity(HomeAssistantEntity):
    device_class = "sensor"
    entity_options = {
        "state_topic": "{}/state",
    }


class SwitchEntity(HomeAssistantEntity):
    device_class = "switch"
    entity_options = {
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }

    def to_hass_state(self) -> str:
        return "ON" if self.initial_state == "ON" else "OFF"


class TextEntity(HomeAssistantEntity):
    device_class = "text"
    entity_options = {
        "command_topic": "{}/set",
        "state_topic": "{}/state",
    }

    def to_hass_state(self) -> str:
        return str(self.initial_state)
