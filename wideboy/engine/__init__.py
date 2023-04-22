import logging
import pygame
from dynaconf import Dynaconf
from pygame import Clock, Surface, RESIZABLE, SCALED, QUIT
from typing import Optional, TYPE_CHECKING
from wideboy.constants import AppMetadata, EVENT_TIMER_SECOND


if TYPE_CHECKING:
    from wideboy.controller import Controller

logger = logging.getLogger("engine")

DISPLAY_FLAGS = RESIZABLE | SCALED
FPS = 60


class Engine:
    controller: "Controller"
    clock: Optional[Clock] = None
    screen: Optional[Surface] = None

    def __init__(self, controller, options: Dynaconf):
        self.controller = controller
        self.options = options
        logger.debug(f"engine:init")
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
            (self.options.display.canvas.width, self.options.display.canvas.height),
            DISPLAY_FLAGS,
        )

    def loop(self):
        # Clock, Blitting, Display
        delta = self.clock_tick()
        events = []
        updates = self.controller.scene_manager.render(self.clock, delta, events)
        pygame.display.update(updates)
        # logger.debug(f"updates={updates}")
        # update_sensors(clock)
        self.controller.display.render(self.screen)
        # Debugging
        self.controller.scene_manager.debug(self.clock, delta)

    def clock_tick(self) -> float:
        self.controller.mqtt.loop(0)
        return self.clock.tick(FPS) / 1000
