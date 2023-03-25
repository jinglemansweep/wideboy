import asyncio
import cProfile
import logging
import pygame
import sys
import traceback
from pygame import QUIT, RESIZABLE, SCALED
from typing import Callable

from wideboy import _APP_DESCRIPTION
from wideboy.utils.helpers import EpochEmitter
from wideboy.utils.mqtt import MQTT, EVENT_MQTT_MESSAGE
from wideboy.utils.hass import EVENT_HASS_COMMAND
from wideboy.config import (
    PROFILING,
)

DISPLAY_FLAGS = RESIZABLE | SCALED

logger = logging.getLogger(__name__)

EVENT_EPOCH_SECOND = pygame.USEREVENT + 11
EVENT_EPOCH_MINUTE = pygame.USEREVENT + 12
EVENT_EPOCH_HOUR = pygame.USEREVENT + 12

FPS = 30

epoch_emitter = EpochEmitter()

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


def clock_tick(clock: pygame.time.Clock) -> float:
    MQTT.loop(0.0001)
    return clock.tick(FPS) / 1000
