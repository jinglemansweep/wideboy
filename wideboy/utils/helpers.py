import cProfile
import pygame
import uuid
import pygame
from typing import Callable
from wideboy.config import settings


def get_unique_device_id(self):
    return uuid.UUID(int=uuid.getnode()).hex[-8:]


def post_event(event_type: str, **kwargs) -> None:
    pygame.event.post(pygame.event.Event(event_type, **kwargs))


def bool_to_hass_state(value: bool) -> str:
    return "ON" if value else "OFF"


def hass_to_bool_state(value: str) -> bool:
    return value == "ON"


def main_entrypoint(main_func: Callable) -> None:
    if settings.general.profiling in ["ncalls", "tottime"]:
        cProfile.run("main_func()", None, sort=settings.general.profiling)
    else:
        main_func()
