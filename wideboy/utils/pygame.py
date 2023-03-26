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
)
from wideboy.config import settings
from wideboy.mqtt import MQTT
from wideboy.utils.helpers import EpochEmitter

DISPLAY_FLAGS = RESIZABLE | SCALED

logger = logging.getLogger(__name__)


FPS = 50

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


def process_pygame_events(events: list[pygame.event.Event]) -> None:
    # Process received messages
    for event in events:
        if event.type == QUIT:
            sys.exit()
    # Post custom messages
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
