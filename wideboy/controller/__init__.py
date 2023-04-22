import logging
import uuid
from typing import Optional
from wideboy.constants import (
    AppMetadata,
    EVENT_MASTER,
    EVENT_SCENE_MANAGER_NEXT,
    EVENT_SCENE_MANAGER_SELECT,
    EVENT_NOTIFICATION_RECEIVED,
    EVENT_ACTION_A,
    EVENT_ACTION_B,
)
from wideboy.display import Display
from wideboy.homeassistant.hass import HASSManager, HASSEntity
from wideboy.homeassistant.mqtt import MQTTClient
from wideboy.engine import Engine
from wideboy.scenes.base import BaseScene
from wideboy.utils.helpers import get_unique_device_id
from wideboy.config import settings

logger = logging.getLogger("controller")


class Controller:
    def __init__(self, scenes: list[BaseScene], entities: list[HASSEntity]):
        self.device_id = settings.general.device_id or get_unique_device_id()
        logger.debug(
            f"controller:init device_id={self.device_id} scenes_count={len(scenes)} entities_count={len(entities)}"
        )
        self.display = Display()
        self.mqtt = MQTTClient(device_id=self.device_id)
        self.hass = HASSManager(self.mqtt, device_id=self.device_id)
        self.engine = Engine(self.display, self.mqtt, self.hass)
        self.setup(scenes, entities)
        self.log_intro()

    def start(self) -> None:
        logger.debug(f"controller:start")
        while True:
            self.engine.loop()

    def setup(self, scenes: list[BaseScene], entities: list[HASSEntity]) -> None:
        self.engine.scene_manager.load_scenes(scenes)
        self.engine.hass.advertise_entities(self.build_internal_entities() + entities)

    def log_intro(self):
        logger.info("=" * 80)
        logger.info(
            f"{AppMetadata.DESCRIPTION} [{AppMetadata.NAME}] v{AppMetadata.VERSION}"
        )
        logger.info("=" * 80)
        logger.info(f"Device ID:   {self.device_id}")
        logger.info(f"Debug:       {settings.general.debug}")
        logger.info(f"Log Level:   {settings.general.log_level}")
        logger.info(
            f"Canvas Size: {settings.display.canvas.width}x{settings.display.canvas.height}"
        )
        logger.info("=" * 80)

    def build_internal_entities(self):
        return [
            HASSEntity(
                "sensor",
                "fps",
                dict(
                    device_class="frequency",
                    suggested_display_precision=1,
                    unit_of_measurement="fps",
                    value_template="{{ value_json.value }}",
                ),
                dict(value=0),
            ),
            HASSEntity(
                "light",
                "master",
                dict(
                    brightness=True,
                    color_mode=True,
                    supported_color_modes=["brightness"],
                ),
                dict(state="ON", brightness=128),
                EVENT_MASTER,
            ),
            HASSEntity("button", "scene_next", event_type=EVENT_SCENE_MANAGER_NEXT),
            HASSEntity("button", "action_a", event_type=EVENT_ACTION_A),
            HASSEntity("button", "action_b", event_type=EVENT_ACTION_B),
            HASSEntity(
                "text", "message", dict(min=1), event_type=EVENT_NOTIFICATION_RECEIVED
            ),
            HASSEntity(
                "select",
                "scene_select",
                dict(
                    options=self.engine.scene_manager.get_scene_names(),
                    value_template="{{ value_json.selected_option }}",
                ),
                dict(selected_option="default"),
                EVENT_SCENE_MANAGER_SELECT,
            ),
        ]
