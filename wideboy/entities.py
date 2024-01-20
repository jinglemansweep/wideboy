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
    power: bool = True
    clock_24_hour: bool = True
    light_state: bool = True
    light_brightness: int = 255
    number_state: float = 5.0
    select_state: str = "Option 1"
    text_state: str = ""
    button_flag: bool = False


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
