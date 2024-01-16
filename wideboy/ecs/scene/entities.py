import datetime
from dataclasses import field
from ecs_pattern import entity
from paho.mqtt.client import Client as MQTTClient
from .components import ComMotion, ComVisible


@entity
class AppState:
    running: bool
    time_now: datetime.datetime = datetime.datetime.now()
    hass_state: dict = field(default_factory=dict)
    events: list = field(default_factory=list)


@entity
class MQTT:
    client: MQTTClient


@entity
class WidgetTest(ComMotion, ComVisible):
    pass


@entity
class WidgetClock(ComVisible):
    pass


@entity
class WidgetHass(ComVisible):
    pass
