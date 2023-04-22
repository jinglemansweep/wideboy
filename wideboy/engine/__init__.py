import json
import logging
import pygame
from dynaconf import Dynaconf
from pygame import Clock, Surface, RESIZABLE, SCALED, QUIT
from typing import Optional, TYPE_CHECKING

from wideboy.config import settings
from wideboy.constants import (
    AppMetadata,
    EVENT_HASS_ENTITY_UPDATE,
    EVENT_TIMER_SECOND,
    EVENT_MASTER,
    EVENT_SCENE_MANAGER_NEXT,
    EVENT_SCENE_MANAGER_SELECT,
)
from wideboy.engine.events import handle_internal_event, handle_joystick_event
from wideboy.engine.scenes import SceneManager
from wideboy.utils.helpers import post_event, hass_to_bool_state

if TYPE_CHECKING:
    from wideboy.homeassistant.hass import HASSManager
    from wideboy.homeassistant.mqtt import MQTTClient
    from wideboy.display import Display

logger = logging.getLogger("engine")

DISPLAY_FLAGS = RESIZABLE | SCALED
FPS = 60


class Engine:
    clock: Optional[Clock] = None
    screen: Optional[Surface] = None

    def __init__(
        self,
        display: "Display",
        mqtt: "MQTTClient",
        hass: "HASSManager",
        fps: int = FPS,
    ):
        self.display = display
        self.mqtt = mqtt
        self.hass = hass
        self.fps = fps
        logger.debug(f"engine:init display={display} mqtt={mqtt} hass={hass} fps={fps}")
        self.scene_manager = SceneManager(engine=self)
        self.joysticks = dict()
        self.setup()

    def setup(self) -> None:
        pygame.init()
        pygame.mixer.quit()
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(QUIT)
        self.clock = Clock()
        pygame.time.set_timer(EVENT_TIMER_SECOND, 1000)
        pygame.display.set_caption(AppMetadata.DESCRIPTION)
        self.screen = pygame.display.set_mode(
            (settings.display.canvas.width, settings.display.canvas.height),
            DISPLAY_FLAGS,
        )

    def loop(self):
        # Clock, Blitting, Display
        delta = self.clock_tick()
        events = pygame.event.get()
        self.process_events(events)
        updates = self.scene_manager.render(self.clock, delta, events)
        pygame.display.update(updates)
        # logger.debug(f"updates={updates}")
        if len(updates) > 0:
            self.display.render(self.screen)
        # Debugging
        self.update_sensors()
        self.scene_manager.debug(self.clock, delta)

    def clock_tick(self) -> float:
        self.mqtt.loop(0)
        return self.clock.tick(self.fps) / 1000

    def update_sensors(self, every_tick: int = 1000):
        if pygame.time.get_ticks() % every_tick == 0:
            post_event(
                EVENT_HASS_ENTITY_UPDATE,
                name="fps",
                state=dict(value=self.clock.get_fps()),
            )

    def process_events(self, events: list[pygame.Event]):
        for event in events:
            handle_internal_event(event)
            handle_joystick_event(event, self.joysticks)
            self.hass.handle_event(event)
            if event.type == EVENT_MASTER:
                payload = json.loads(event.payload)
                self.display.set_visible(hass_to_bool_state(payload["state"]))
                if "brightness" in payload:
                    self.display.set_brightness(payload["brightness"])
            if event.type == EVENT_SCENE_MANAGER_NEXT:
                self.scene_manager.next_scene()
            if event.type == EVENT_SCENE_MANAGER_SELECT:
                self.scene_manager.change_scene(event.payload)
