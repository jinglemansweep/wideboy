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
    time_now: datetime.datetime = datetime.datetime.now()
    hass_state: dict = field(default_factory=dict)
    power: bool = True


@entity
class MQTTService:
    client: MQTTClient
    listeners: list = field(default_factory=list)


@entity
class WidgetTest(ComMotion, ComVisible):
    pass


@entity
class WidgetClock(ComVisible):
    pass


@entity
class WidgetTileGrid(ComMotion, ComVisible):
    pass
