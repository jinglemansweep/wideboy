import logging
import uuid
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

    def load_scenes(self, scenes: list):
        self.engine.scene_manager.load_scenes(scenes)

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
