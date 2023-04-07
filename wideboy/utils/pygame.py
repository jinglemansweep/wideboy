import asyncio
import cProfile
import logging
import pygame
import sys
import traceback
from pygame import QUIT, RESIZABLE, SCALED
from typing import Callable

from wideboy.constants import (
    AppMetadata,
    EVENT_EPOCH_SECOND,
    EVENT_EPOCH_MINUTE,
    EVENT_EPOCH_HOUR,
    EVENT_SCENE_MANAGER_NEXT,
    GAMEPAD,
)
from wideboy.config import settings
from wideboy.mqtt import MQTT
from wideboy.mqtt import handle_mqtt_event
from wideboy.state import handle_state_event
from wideboy.scenes.manager import SceneManager
from wideboy.utils.helpers import EpochEmitter

logger = logging.getLogger("utils.pygame")

DISPLAY_FLAGS = RESIZABLE | SCALED
FPS = 50
JOYSTICKS = dict()

epoch_emitter = EpochEmitter()


def setup_pygame(
    display_size: pygame.math.Vector2,
) -> tuple[pygame.time.Clock, pygame.surface.Surface]:

    pygame.init()
    pygame.mixer.quit()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(QUIT)
    clock = pygame.time.Clock()
    pygame.display.set_caption(AppMetadata.DESCRIPTION)
    screen = pygame.display.set_mode(display_size, DISPLAY_FLAGS)
    return clock, screen


def handle_events(
    events: list[pygame.event.Event], matrix: any, scene_manager: SceneManager
) -> None:
    pump_epoch_events()
    for event in events:
        # Input Events
        handle_internal_event(event)
        handle_mqtt_event(event)
        handle_joystick_event(event)
        # State Events
        handle_state_event(event, matrix)
        # Scene Events
        scene_manager.handle_event(event)


def handle_internal_event(event: pygame.event.Event) -> None:
    # PyGame internal events
    if event.type == pygame.QUIT:
        sys.exit()


def pump_epoch_events() -> None:
    epochs = epoch_emitter.check()
    if epochs.get("new_sec"):
        pygame.event.post(
            pygame.event.Event(EVENT_EPOCH_SECOND, unit=epochs.get("sec"))
        )
    if epochs.get("new_min"):
        pygame.event.post(
            pygame.event.Event(EVENT_EPOCH_MINUTE, unit=epochs.get("min"))
        )
    if epochs.get("new_hour"):
        pygame.event.post(pygame.event.Event(EVENT_EPOCH_HOUR, unit=epochs.get("hour")))


def handle_joystick_event(event: pygame.event.Event) -> None:
    if event.type == pygame.JOYDEVICEADDED:
        joystick = pygame.joystick.Joystick(event.device_index)
        logger.debug(
            f"joystick:added device_index={event.device_index} instance_id={joystick.get_instance_id()}"
        )
        JOYSTICKS[joystick.get_instance_id()] = joystick
    elif event.type == pygame.JOYDEVICEREMOVED:
        del JOYSTICKS[event.instance_id]
        logger.debug(f"joystick:removed instance_id={event.instance_id}")
    if event.type == pygame.JOYBUTTONUP:
        logger.debug(f"joystick action=BUTTONUP button={event.button}")
        if event.button in [GAMEPAD["BUTTON_L"], GAMEPAD["BUTTON_R"]]:
            pygame.event.post(pygame.event.Event(EVENT_SCENE_MANAGER_NEXT))
    if event.type == pygame.JOYHATMOTION:
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
    MQTT.loop(0.0001)
    return clock.tick(FPS) / 1000
