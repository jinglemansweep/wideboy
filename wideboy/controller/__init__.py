from wideboy.controller.display import Display
from wideboy.controller.mqtt import MQTTClient
from wideboy.controller.homeassistant import HASSManager
from wideboy.controller.engine import Engine


class Controller:
    def __init__(self, settings: dict):
        self.display = Display(options=settings.display)
        self.mqtt = MQTTClient(options=settings.mqtt)
        self.hass = HASSManager(options=settings.homeassistant)
        self.engine = Engine(options=settings)
