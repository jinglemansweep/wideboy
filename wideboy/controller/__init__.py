import logging
import uuid
from typing import Optional
from wideboy.constants import AppMetadata
from wideboy.display import Display
from wideboy.homeassistant import HASSManager
from wideboy.engine import Engine
from wideboy.scenes.base import BaseScene
from wideboy.utils.helpers import get_unique_device_id
from wideboy.config import settings

logger = logging.getLogger("controller")


class Controller:
    def __init__(self, scenes: list):
        self.device_id = settings.general.device_id or get_unique_device_id()
        logger.debug(f"controller:init device_id={self.device_id} scenes={scenes}")
        self.display = Display()
        self.hass = HASSManager(device_id=self.device_id)
        self.engine = Engine(self.display, self.hass)
        self.setup(scenes)
        self.log_intro()

    def start(self) -> None:
        logger.debug(f"controller:start")
        while True:
            self.engine.loop()

    def setup(self, scenes: list[BaseScene]) -> None:
        self.load_scenes(scenes)
        self.advertise_hass_entities()

    def load_scenes(self, scenes: list):
        self.engine.scene_manager.load_scenes(scenes)

    def advertise_hass_entities(self):
        self.engine.hass.advertise_entity(
            "master",
            "light",
            dict(
                brightness=True, color_mode=True, supported_color_modes=["brightness"]
            ),
            dict(state="ON", brightness=128),
        )
        self.engine.hass.advertise_entity("scene_next", "button")
        self.engine.hass.advertise_entity(
            "fps",
            "sensor",
            dict(
                device_class="frequency",
                suggested_display_precision=1,
                unit_of_measurement="fps",
                value_template="{{ value_json.value }}",
            ),
            initial_state=dict(value=0),
        )
        self.engine.hass.advertise_entity("action_a", "button")
        self.engine.hass.advertise_entity("action_b", "button")
        self.engine.hass.advertise_entity("message", "text", dict(min=1))
        self.engine.hass.advertise_entity(
            "scene_select",
            "select",
            dict(
                options=self.engine.scene_manager.get_scene_names(),
                value_template="{{ value_json.selected_option }}",
            ),
            initial_state=dict(selected_option="default"),
        )

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
