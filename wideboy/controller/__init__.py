import logging
import uuid
from wideboy.constants import AppMetadata
from wideboy.display import Display
from wideboy.mqtt import MQTTClient
from wideboy.homeassistant import HASSManager
from wideboy.engine import Engine
from wideboy.engine.scenes import SceneManager
from wideboy.scenes.base import BaseScene
from wideboy.utils.helpers import get_unique_device_id

logger = logging.getLogger("controller")


class Controller:
    def __init__(self, settings: dict, scenes: list):
        logger.debug(f"controller:init settings={settings} scenes={scenes}")
        self.settings = settings
        self.display = Display(options=settings.display)
        self.mqtt = MQTTClient(controller=self, options=settings.mqtt)
        self.hass = HASSManager(options=settings.homeassistant)
        self.scene_manager = SceneManager(controller=self)
        self.engine = Engine(controller=self, options=settings)
        self.setup(scenes)
        self.log_intro()

    def start(self) -> None:
        logger.debug(f"controller:start")
        while True:
            self.engine.loop()

    def setup(self, scenes: list[BaseScene]) -> None:
        self.device_id = self.settings.general.device_id or get_unique_device_id()
        self.load_scenes(scenes)

    def load_scenes(self, scenes: list):
        self.scene_manager.load_scenes(scenes)

    def log_intro(self):
        logger.info("=" * 80)
        logger.info(
            f"{AppMetadata.DESCRIPTION} [{AppMetadata.NAME}] v{AppMetadata.VERSION}"
        )
        logger.info("=" * 80)
        logger.info(f"Device ID:   {self.device_id}")
        logger.info(f"Debug:       {self.settings.general.debug}")
        logger.info(f"Log Level:   {self.settings.general.log_level}")
        logger.info(
            f"Canvas Size: {self.settings.display.canvas.width}x{self.settings.display.canvas.height}"
        )
        logger.info("=" * 80)
