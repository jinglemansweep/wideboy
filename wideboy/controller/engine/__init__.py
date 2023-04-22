import logging
import pygame
from dynaconf import Dynaconf
from pygame import Clock, Surface, RESIZABLE, SCALED, QUIT
from typing import Optional
from wideboy.constants import AppMetadata, EVENT_TIMER_SECOND

logger = logging.getLogger("controller.engine")

DISPLAY_FLAGS = RESIZABLE | SCALED


class Engine:
    clock: Optional[Clock] = None
    screen: Optional[Surface] = None

    def __init__(self, options: Dynaconf):
        self.options = options
        logger.info(f"Engine")
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
