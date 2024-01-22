import datetime
from dataclasses import field
from dynaconf import Dynaconf
from ecs_pattern import entity
from paho.mqtt.client import Client as MQTTClient
from typing import Callable
from .components import ComMotion, ComTarget, ComVisible


@entity
class AppState:
    booting: bool
    running: bool
    config: Dynaconf = None
    events: list = field(default_factory=list)
    time_now: datetime.datetime = datetime.datetime.now()
    hass_state: dict = field(default_factory=dict)
    master_power: bool = True
    master_brightness: int = 128
    background_interval: int = 1
    clock_24_hour: bool = True
    text_message: str = ""
    scene_mode: str = "default"


@entity
class MQTTService:
    client: MQTTClient
    connect_callback: Callable
    on_connect_listeners: list = field(default_factory=list)
    on_disconnect_listeners: list = field(default_factory=list)
    on_message_listeners: list = field(default_factory=list)


@entity
class Cache:
    surfaces: dict = field(default_factory=dict)


@entity
class WidgetText(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetSquare(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetImage(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetSysMessage(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetClockBackground(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetClockDate(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetClockTime(ComTarget, ComMotion, ComVisible):
    pass


@entity
class WidgetTileGrid(ComTarget, ComMotion, ComVisible):
    pass
