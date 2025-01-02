import datetime
from dataclasses import field
from dynaconf import Dynaconf
from ecs_pattern import entity
from paho.mqtt.client import Client as MQTTClient
from typing import Callable
from .components import (
    ComAlpha,
    ComBound,
    ComFade,
    ComFrame,
    ComMotion,
    ComTarget,
    ComVisible,
)


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
    tint_enabled: bool = False
    tint_brightness: int = 128
    tint_color: tuple = (255, 0, 64)
    slideshow_interval: int = 10
    slideshow_index: int = 0
    clock_24_hour: bool = True
    screenshot: bool = False
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
class WidgetText(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetSquare(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetImage(ComFade, ComBound, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetFrameAnimation(
    ComFrame, ComFade, ComBound, ComTarget, ComMotion, ComAlpha, ComVisible
):
    pass


@entity
class WidgetSysMessage(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetClockBackground(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetClockDate(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetClockTime(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetTileGrid(ComFade, ComTarget, ComMotion, ComAlpha, ComVisible):
    pass


@entity
class WidgetSlideshow(ComVisible):
    pass
