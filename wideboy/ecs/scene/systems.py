from pygame import Event, Surface
from pygame.constants import (
    KEYDOWN,
    KEYUP,
    K_DOWN,
    K_ESCAPE,
    K_UP,
    QUIT,
)
from pygame.event import get as get_events, post as post_event
from pygame.display import Info as DisplayInfo
from paho.mqtt.client import Client as MQTTClient
from ecs_pattern import EntityManager, System
import datetime
from .components import ComMotion, ComVisible
from .consts import EVENT_HASS_ENTITY_UPDATE
from .sprites import clock_sprite, test_sprite
from .entities import (
    AppState,
    MQTT,
    WidgetClock,
    WidgetTest,
    WidgetTileGrid,
)

from ...sprites.tile_grid_ecs import TileGrid
from ...scenes.default.tiles import CELLS


class SysInit(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def start(self):
        self.entities.init()
        app_state = AppState(running=True)
        self.entities.add(app_state)
        self.entities.add(
            WidgetClock(clock_sprite(""), 0, 0),
            WidgetTest(test_sprite(), 100, 100, 1, 1),
            WidgetTileGrid(TileGrid(CELLS, app_state.hass_state), 20, 50),
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
            # print("NEW SECOND")
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
            post_event(
                Event(
                    EVENT_HASS_ENTITY_UPDATE,
                    dict(entity_id=entity_id_full, attribute=attr, payload=payload),
                )
            )
            if entity_id_full not in app_state.hass_state:
                app_state.hass_state[entity_id_full] = dict()
            app_state.hass_state[entity_id_full][attr] = payload


class SysEvents(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def update(self):
        for event in get_events():
            if event.type == EVENT_HASS_ENTITY_UPDATE:
                widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
                widget_tilegrid.sprite.update(event.entity_id)


class SysInputControl(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.event_types = (KEYDOWN, KEYUP, QUIT)  # Whitelist
        self.app_state = None

    def start(self):
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self):
        for event in get_events(self.event_types):
            event_type = event.type
            event_key = getattr(event, "key", None)
            # Quit App
            if (event_type == KEYDOWN and event_key == K_ESCAPE) or event_type == QUIT:
                self.app_state.running = False
            # Up/Down
            if event_type == KEYDOWN and event_key in (K_UP, K_DOWN):
                print("Up/Down", event_key)


class SysMovement(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.app_state = None

    def start(self):
        self.display_info = DisplayInfo()
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self):
        # TODO: move somewhere else
        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_tilegrid.sprite.update()
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
