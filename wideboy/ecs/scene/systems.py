from pygame import Event, Surface
from pygame.constants import (
    KEYDOWN,
    KEYUP,
    K_DOWN,
    K_ESCAPE,
    K_UP,
    QUIT,
)
from pygame.display import Info as DisplayInfo
from paho.mqtt.client import Client as MQTTClient
from ecs_pattern import EntityManager, System
import datetime
from typing import Callable
from .components import ComMotion, ComVisible
from .consts import EventsEnum
from .sprites import clock_sprite, test_sprite
from .entities import AppState, MQTT, WidgetClock, WidgetHass, WidgetTest

from ...sprites.tile_grid_ecs import TileGrid
from ...scenes.default.tiles import CELLS


class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        self.entities.init()
        self.entities.add(
            AppState(running=True),
            WidgetClock(clock_sprite(""), 0, 0),
            WidgetTest(test_sprite(), 100, 100, 1, 1),
            WidgetHass(TileGrid(CELLS), 20, 50),
            # GameStateInfo(play=True, pause=False),
            # WaitForBallMoveEvent(1000),
        )


class SysClock(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.now = datetime.datetime.now()

    def start(self):
        pass

    def update(self):
        now = datetime.datetime.now()
        if now.second != self.now.second:
            print("NEW SECOND")
            self.now = now
            self.set_clock()

    def set_clock(self):
        app_state = next(self.entities.get_by_class(AppState))
        app_state.time_now = self.now
        clock = next(self.entities.get_by_class(WidgetClock))
        clock.sprite = clock_sprite(app_state.time_now.strftime("%H:%M:%S"))


class SysMqttControl(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.client = MQTTClient()

    def start(self):
        self.client.username_pw_set("mqtt", "password")
        self.client.on_message = self._on_message
        self.client.connect("hass.home", 1883, 60)
        self.client.subscribe("homeassistant/statestream/#")
        self.entities.add(MQTT(client=self.client))

    def update(self):
        self.client.loop(timeout=0.001)

    def _on_message(self, client, userdata, message):
        topic_prefix = "homeassistant/statestream"
        app_state = next(self.entities.get_by_class(AppState))
        if message.topic.startswith(f"{topic_prefix}/") and message.payload:
            parts = message.topic[len(topic_prefix) :].split("/")
            payload = message.payload.decode("utf-8")
            device_class, entity_id, attr = parts[1], parts[-2], parts[-1]
            entity_id_full = f"{device_class}.{entity_id}"
            app_state.events.append(
                (EventsEnum.HASS_ENTITY_UPDATE, (entity_id_full, attr, payload))
            )
            if entity_id_full not in app_state.hass_state:
                app_state.hass_state[entity_id_full] = dict()
            app_state.hass_state[entity_id_full][attr] = payload


class SysInputControl(System):
    def __init__(
        self, entities: EntityManager, event_getter: Callable[..., list[Event]]
    ):
        self.entities = entities
        self.event_getter = event_getter
        self.event_types = (KEYDOWN, KEYUP, QUIT)  # Whitelist
        self.app_state = None

    def start(self):
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self):
        for event in self.event_getter(self.event_types):
            event_type = event.type
            event_key = getattr(event, "key", None)
            # Quit App
            if (event_type == KEYDOWN and event_key == K_ESCAPE) or event_type == QUIT:
                self.app_state.running = False
            # Up/Down
            if event_type == KEYDOWN and event_key in (K_UP, K_DOWN):
                print("Up/Down", event_key)


class SysEventBus(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.app_state = None

    def start(self):
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self):
        if len(self.app_state.events) > 0:
            print(len(self.app_state.events))
            event, payload = self.app_state.events.pop(0)
            if event == EventsEnum.HASS_ENTITY_UPDATE:
                hass_widget = next(self.entities.get_by_class(WidgetHass))
                hass_widget.sprite.update(payload[0])


class SysMovement(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.app_state = None

    def start(self):
        self.display_info = DisplayInfo()
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self):
        # TODO: move somewhere else
        hass_widget = next(self.entities.get_by_class(WidgetHass))
        hass_widget.sprite.state = self.app_state.hass_state
        hass_widget.sprite.update()
        # get entities
        test_entity = next(self.entities.get_by_class(WidgetTest))
        # move
        for movable_entity in self.entities.get_with_component(ComMotion, ComVisible):
            movable_entity.x += movable_entity.speed_x
            movable_entity.y += movable_entity.speed_y
        # ball reflect
        # print(test_entity.x, test_entity.y, test_entity.speed_x, test_entity.speed_y)
        if test_entity.x < 0:
            test_entity.speed_x = -test_entity.speed_x
        if test_entity.x > self.display_info.current_w:
            test_entity.speed_x = -test_entity.speed_x
        if test_entity.y < 0:
            test_entity.speed_y = -test_entity.speed_y
        if test_entity.y > self.display_info.current_h:
            test_entity.speed_y = -test_entity.speed_y


class SysDraw(System):
    def __init__(self, entities: EntityManager, screen: Surface):
        self.entities = entities
        self.screen = screen

    def update(self):
        self.screen.fill((0, 0, 0))
        for visible_entity in self.entities.get_with_component(ComVisible):
            self.screen.blit(
                visible_entity.sprite.image, (visible_entity.x, visible_entity.y)
            )
