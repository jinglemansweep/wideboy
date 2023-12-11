import logging
import pygame
import sys
from datetime import datetime
from pygame import (
    Event,
    Joystick,
    QUIT,
    JOYDEVICEADDED,
    JOYDEVICEREMOVED,
    JOYBUTTONUP,
    JOYHATMOTION,
)
from wideboy.constants import (
    EVENT_TIMER_SECOND,
    EVENT_EPOCH_SECOND,
    EVENT_EPOCH_MINUTE,
    EVENT_EPOCH_HOUR,
    EVENT_SCENE_MANAGER_NEXT,
    GAMEPAD,
)
from typing import Any, Dict

logger = logging.getLogger("events")


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


def handle_joystick_event(event: pygame.event.Event, joysticks: Dict[int, Any]) -> None:
    if event.type == JOYDEVICEADDED:
        joystick = Joystick(event.device_index)
        logger.debug(
            f"joystick:added device_index={event.device_index} instance_id={joystick.get_instance_id()}"
        )
        joysticks[joystick.get_instance_id()] = joystick
    elif event.type == JOYDEVICEREMOVED:
        del joysticks[event.instance_id]
        logger.debug(f"joystick:removed instance_id={event.instance_id}")
    if event.type == JOYBUTTONUP:
        logger.debug(f"joystick action=BUTTONUP button={event.button}")
        if event.button in [GAMEPAD["BUTTON_L"], GAMEPAD["BUTTON_R"]]:
            pygame.event.post(Event(EVENT_SCENE_MANAGER_NEXT))
    if event.type == JOYHATMOTION:
        logger.debug(f"Joystick action=HATMOTION hat={event.hat} value={event.value}")
