import asyncio
import logging
import os
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy import _APP_NAME
from wideboy.config import LOG_DEBUG, CANVAS_SIZE, MATRIX_ENABLED
from wideboy.utils.display import setup_led_matrix, render_led_matrix
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
if MATRIX_ENABLED:
    matrix, matrix_buffer = setup_led_matrix()

# Loop Setup

running = True

# Scratch Area


class Stage:
    def __init__(self, dest: pygame.surface.Surface, color_bg=(0, 0, 0)) -> None:
        self.dest = dest
        width, height = dest.get_width(), dest.get_height()
        self.background = pygame.surface.Surface((width, height))
        self.background.fill(color_bg)
        self.group = pygame.sprite.LayeredDirty()
        self.clock = ClockWidgetSprite(
            (width - 128, 0, 128, height),
            color_bg=(128, 0, 0, 192),
        )
        self.group.add(self.clock)

    def render(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.dest, self.background)

    def update(self, *args, **kwargs) -> None:
        self.group.update(*args, **kwargs)

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.dest)


# Main Loop


async def start_main_loop():

    global matrix, matrix_buffer

    loop = asyncio.get_event_loop()

    stage = Stage(screen, color_bg=(0, 0, 64, 255))

    while running:
        for event in pygame.event.get():
            handle_event(event)

        frame, delta = clock_tick(clock)

        stage_updates = stage.render(frame, delta)
        updates = [] + stage_updates
        if len(updates):
            logger.debug(f"display:draw rects={len(updates)}")
        pygame.display.update(updates)
        if MATRIX_ENABLED:
            matrix_buffer = render_led_matrix(matrix, screen, matrix_buffer)
        loop_debug(
            frame,
            clock,
            delta,
        )
        await asyncio.sleep(0)


# Entrypoint

if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
