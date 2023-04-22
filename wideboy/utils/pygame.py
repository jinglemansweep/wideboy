import asyncio
import cProfile
import logging
import pygame
import sys
import traceback
from datetime import datetime
from pygame import (
    Clock,
    Event,
    Surface,
    Vector2,
    QUIT,
    RESIZABLE,
    SCALED,
    JOYDEVICEADDED,
    JOYDEVICEREMOVED,
    JOYBUTTONUP,
    JOYHATMOTION,
)
from pygame.joystick import Joystick
from typing import Callable

from wideboy.constants import (
    AppMetadata,
    EVENT_EPOCH_SECOND,
    EVENT_EPOCH_MINUTE,
    EVENT_EPOCH_HOUR,
    EVENT_TIMER_SECOND,
    EVENT_SCENE_MANAGER_NEXT,
    GAMEPAD,
)
from wideboy.config import settings

logger = logging.getLogger("utils.pygame")

DISPLAY_FLAGS = RESIZABLE | SCALED
FPS = 60
JOYSTICKS = dict()


def dispatch_event(event: Event) -> None:
    handle_internal_event(event)
    # handle_mqtt_event(event)
    handle_joystick_event(event)


def handle_internal_event(event: Event) -> None:
    if event.type == QUIT:
        sys.exit()
    if event.type == EVENT_TIMER_SECOND:
        now = datetime.now()
        pygame.event.post(Event(EVENT_EPOCH_SECOND, unit=now.second, now=now))
        if now.second == 0:
            pygame.event.post(Event(EVENT_EPOCH_MINUTE, unit=now.minute, now=now))
            if now.minute == 0:
                pygame.event.post(Event(EVENT_EPOCH_HOUR, unit=now.hour, now=now))


def handle_joystick_event(event: pygame.event.Event) -> None:
    if event.type == JOYDEVICEADDED:
        joystick = Joystick(event.device_index)
        logger.debug(
            f"joystick:added device_index={event.device_index} instance_id={joystick.get_instance_id()}"
        )
        JOYSTICKS[joystick.get_instance_id()] = joystick
    elif event.type == JOYDEVICEREMOVED:
        del JOYSTICKS[event.instance_id]
        logger.debug(f"joystick:removed instance_id={event.instance_id}")
    if event.type == JOYBUTTONUP:
        logger.debug(f"joystick action=BUTTONUP button={event.button}")
        if event.button in [GAMEPAD["BUTTON_L"], GAMEPAD["BUTTON_R"]]:
            pygame.event.post(Event(EVENT_SCENE_MANAGER_NEXT))
    if event.type == JOYHATMOTION:
        logger.debug(f"Joystick action=HATMOTION hat={event.hat} value={event.value}")
