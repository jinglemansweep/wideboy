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
from wideboy.mqtt import MQTT
from wideboy.mqtt import handle_mqtt_event

logger = logging.getLogger("utils.pygame")

DISPLAY_FLAGS = RESIZABLE | SCALED
FPS = 120
JOYSTICKS = dict()


def setup_pygame(
    display_size: Vector2,
) -> tuple[Clock, Surface]:
    pygame.init()
    pygame.mixer.quit()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(QUIT)
    clock = Clock()
    pygame.time.set_timer(EVENT_TIMER_SECOND, 1000)
    pygame.display.set_caption(AppMetadata.DESCRIPTION)
    screen = pygame.display.set_mode(display_size, DISPLAY_FLAGS)
    return clock, screen


def dispatch_event(event: Event) -> None:
    handle_internal_event(event)
    handle_mqtt_event(event)
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


def main_entrypoint(main_func: Callable) -> None:
    if settings.general.profiling in ["ncalls", "tottime"]:
        cProfile.run("main_func()", None, sort=settings.general.profiling)
    else:
        main_func()


def run_loop(loop_func: Callable) -> None:
    while True:
        try:
            asyncio.run(loop_func())
        except Exception as e:
            logging.error(traceback.format_exc())


def clock_tick(clock: pygame.time.Clock) -> float:
    MQTT.loop(0)
    return clock.tick(FPS) / 1000
