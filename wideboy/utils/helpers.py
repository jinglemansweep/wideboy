import pygame
import uuid
from typing import Any


def get_unique_device_id() -> str:
    return uuid.UUID(int=uuid.getnode()).hex[-8:]


def post_event(event_type: int, **kwargs: Any) -> None:
    pygame.event.post(pygame.event.Event(event_type, **kwargs))


def bool_to_hass_state(value: bool) -> str:
    return "ON" if value else "OFF"


def hass_to_bool_state(value: str) -> bool:
    return value == "ON"
