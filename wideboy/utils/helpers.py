import aiohttp
import async_timeout
import uuid
import logging
import pygame
import random
from datetime import datetime
from typing import Any, Optional
from wideboy import _APP_NAME, _APP_DESCRIPTION, _APP_VERSION
from wideboy.config import DEBUG, LOG_DEBUG, CANVAS_SIZE

logger = logging.getLogger(__name__)


def intro_debug() -> None:
    logger.info("=" * 80)
    logger.info(f"{_APP_DESCRIPTION} [{_APP_NAME}] v{_APP_VERSION}")
    logger.info("=" * 80)
    logger.info(f"Debug:       {DEBUG}")
    logger.info(f"Log Debug:   {LOG_DEBUG}")
    logger.info(f"Canvas Size: {CANVAS_SIZE[0]}x{CANVAS_SIZE[1]}")
    logger.info("=" * 80)


def random_color() -> pygame.color.Color:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


async def async_fetch(session: aiohttp.ClientSession, url: str) -> str:
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


def get_device_id() -> str:
    return uuid.UUID(int=uuid.getnode()).hex[-8:]


class EpochEmitter:
    def __init__(self) -> None:
        self._update()

    def check(self, unit=None) -> Any:
        now = datetime.timetuple(datetime.now())
        is_new_sec = now.tm_sec != self.then.tm_sec
        is_new_min = now.tm_min != self.then.tm_min
        is_new_hour = now.tm_hour != self.then.tm_hour
        is_new_mday = now.tm_mday != self.then.tm_mday
        epochs = dict(
            sec=now.tm_sec,
            min=now.tm_min,
            hour=now.tm_hour,
            mday=now.tm_mday,
            new_sec=is_new_sec,
            new_min=is_new_min,
            new_hour=is_new_hour,
            new_mday=is_new_mday,
        )
        self._update()
        if unit is not None:
            return epochs.get(unit)
        else:
            return epochs

    def _update(self) -> None:
        self.then = datetime.timetuple(datetime.now())


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
