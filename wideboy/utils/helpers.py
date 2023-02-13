import aiohttp
import async_timeout
import asyncio
import logging
import os
import pathlib
import pygame
import random
from typing import Any, Optional
from wideboy import _APP_NAME, _APP_DESCRIPTION, _APP_VERSION
from wideboy.config import DEBUG, FT_SIZE

logger = logging.getLogger(__name__)


def intro_debug() -> None:
    logger.info("=" * 80)
    logger.info(f"{_APP_DESCRIPTION} [{_APP_NAME}] v{_APP_VERSION}")
    logger.info("=" * 80)
    logger.info(f"Debug: {DEBUG}")
    logger.info(f"FT Panel Size: {FT_SIZE[0]}x{FT_SIZE[1]}")
    logger.info("=" * 80)


def random_color() -> tuple[int, int, int]:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


def get_config_env_var(
    key: str, default: Any = None, namespace: Optional[str] = None
) -> Optional[str]:
    if namespace is not None:
        key = f"{namespace}_{key}".upper()
    value = os.environ.get(key, default)
    logger.debug(f"config:env key={key} value={value}")
    return value


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
