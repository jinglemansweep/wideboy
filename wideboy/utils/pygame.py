import asyncio
import cProfile
import logging
import pygame
import sys
import traceback
from pygame import QUIT, DOUBLEBUF, RESIZABLE, SCALED
from typing import Callable

from wideboy import _APP_DESCRIPTION
from wideboy.utils.helpers import EpochEmitter
from wideboy.utils.mqtt import EVENT_MQTT_MESSAGE
from wideboy.utils.hass import EVENT_HASS_COMMAND
from wideboy.utils.state import state, StateStore
from wideboy.config import (
    PROFILING,
)

DISPLAY_FLAGS = RESIZABLE  # | SCALED | DOUBLEBUF

logger = logging.getLogger(__name__)

EVENT_EPOCH_SECOND = pygame.USEREVENT + 11
EVENT_EPOCH_MINUTE = pygame.USEREVENT + 12

epoch_emitter = EpochEmitter()

frame = 0


def setup_pygame(
    display_size: tuple[int, int]
) -> tuple[pygame.time.Clock, pygame.surface.Surface]:

    pygame.init()
    pygame.mixer.quit()
    pygame.event.set_allowed(None)
    pygame.event.set_allowed(QUIT)
    clock = pygame.time.Clock()
    pygame.display.set_caption(_APP_DESCRIPTION)
    screen = pygame.display.set_mode(display_size, DISPLAY_FLAGS)
    return clock, screen


def process_pygame_events(events: list[pygame.event.Event]) -> None:
    # Process received messages
    for event in events:
        handle_event(event)
    # Post custom messages
    epochs = epoch_emitter.check()
    if epochs.get("sec"):
        pygame.event.post(pygame.event.Event(EVENT_EPOCH_SECOND))
    if epochs.get("min"):
        pygame.event.post(pygame.event.Event(EVENT_EPOCH_MINUTE))


def handle_event(event: pygame.event.Event) -> None:
    if event.type == QUIT:
        sys.exit()
    if event.type == EVENT_MQTT_MESSAGE:
        # logger.debug(f"MQTT MESSAGE: Topic: {event.topic} Payload: {event.payload}")
        pass


def main_entrypoint(main_func: Callable) -> None:
    if PROFILING in ["ncalls", "tottime"]:
        cProfile.run("main_func()", None, sort=PROFILING)
    else:
        main_func()


def run_loop(loop_func: Callable) -> None:
    while True:
        try:
            asyncio.run(loop_func())
        except Exception as e:
            logging.error(traceback.format_exc())


def loop_debug(
    frame: int,
    clock: pygame.time.Clock,
    delta: float,
    state: StateStore,
    every: int = 200,
) -> None:
    if frame % every == 0:
        logger.info(
            f"loop:debug frame={frame} fps={clock.get_fps()} delta={delta} state={state}"
        )


def clock_tick(clock: pygame.time.Clock) -> tuple[int, float]:
    global frame
    delta = clock.tick() / 1000
    frame += 1
    return frame, delta
