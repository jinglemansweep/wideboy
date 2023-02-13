import asyncio
import logging
import os
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy import _APP_NAME
from wideboy.config import DEBUG, LOG_DEBUG, CANVAS_SIZE
from wideboy.utils.helpers import (
    intro_debug,
)
from wideboy.utils.logger import setup_logger
from wideboy.utils.pygame import (
    setup_pygame,
    handle_event,
    main_entrypoint,
    run_loop,
    loop_debug,
    clock_tick,
)
from wideboy.sprites.clock import ClockWidgetSprite

# Logging

setup_logger(debug=LOG_DEBUG)
logger = logging.getLogger(_APP_NAME)

# Startup

intro_debug()

# PyGame & Display

clock, screen = setup_pygame(CANVAS_SIZE)

# Loop Setup

running = True

# Scratch Area


class Stage:
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.screen = screen
        self.background = pygame.surface.Surface(CANVAS_SIZE)
        self.background.fill((0, 0, 0, 255))
        self.group = pygame.sprite.LayeredDirty()
        self.clock = ClockWidgetSprite(
            (CANVAS_SIZE[0] - 128, 0, 128, CANVAS_SIZE[1]),
            color_bg=(128, 0, 0, 192),
        )
        self.group.add(self.clock)

    def render(self, *args, **kwargs) -> None:
        self._update(*args, **kwargs)
        self._clear()
        return self._draw()

    def _update(self, *args, **kwargs) -> None:
        self.group.update(*args, **kwargs)

    def _clear(self) -> None:
        self.group.clear(self.screen, self.background)

    def _draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(screen)


# Main Loop


async def start_main_loop():

    loop = asyncio.get_event_loop()

    stage = Stage(screen)

    while running:
        for event in pygame.event.get():
            handle_event(event)

        frame, delta = clock_tick(clock)

        stage_updates = stage.render(frame, delta)
        updates = [] + stage_updates
        if len(updates):
            logger.debug(f"display:updates rects={len(updates)}")
        pygame.display.update(updates)

        loop_debug(
            frame,
            clock,
            delta,
        )
        await asyncio.sleep(0)


# Entrypoint

if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
