import datetime
from dataclasses import field
from dynaconf import Dynaconf
from ecs_pattern import entity
from paho.mqtt.client import Client as MQTTClient
from .components import ComMotion, ComVisible


@entity
class AppState:
    running: bool
    config: Dynaconf = None
    events: list = field(default_factory=list)
    time_now: datetime.datetime = datetime.datetime.now()
    hass_state: dict = field(default_factory=dict)
    master_power: bool = True
    master_brightness: int = 255
    background_interval: int = 1
    clock_24_hour: bool = True
    text_message: str = ""
    scene_mode: str = "default"


@entity
class MQTTService:
    client: MQTTClient
    listeners: list = field(default_factory=list)


@entity
class WidgetTest(ComMotion, ComVisible):
    pass


@entity
class WidgetClockDate(ComVisible):
    pass


@entity
class WidgetClockTime(ComVisible):
    pass


@entity
class WidgetTileGrid(ComVisible):
    pass
