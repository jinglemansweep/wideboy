import aiohttp
import async_timeout
import logging

import pygame
import random
from typing import Any, Optional
from wideboy import _APP_NAME, _APP_DESCRIPTION, _APP_VERSION
from wideboy.config import DEBUG, CANVAS_SIZE

logger = logging.getLogger(__name__)


def intro_debug() -> None:
    logger.info("=" * 80)
    logger.info(f"{_APP_DESCRIPTION} [{_APP_NAME}] v{_APP_VERSION}")
    logger.info("=" * 80)
    logger.info(f"Debug: {DEBUG}")
    logger.info(f"Canvas Size: {CANVAS_SIZE[0]}x{CANVAS_SIZE[1]}")
    logger.info("=" * 80)


def random_color() -> tuple[int, int, int]:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


class JoyPad:
    def __init__(self, device_index: int) -> None:
        pygame.joystick.init()
        self.joypad = pygame.joystick.Joystick(device_index)
        self.joypad.init()
        self.button = None
        self.direction = (0, 0)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.JOYBUTTONDOWN:
            self.button = event.dict["button"]
        if event.type == pygame.JOYHATMOTION:
            self.direction = event.dict["value"]
