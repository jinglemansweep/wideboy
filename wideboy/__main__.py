import asyncio
import json
import logging
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy.constants import AppMetadata
from wideboy.config import (
    settings,
)
from wideboy.mqtt import MQTT, EVENT_MQTT_MESSAGE
from wideboy.mqtt.entities import HASS_MASTER, HASS_ACTION_SCENE_NEXT
from wideboy.mqtt.homeassistant import setup_hass
from wideboy.scenes.manager import SceneManager
from wideboy.state import STATE, DEVICE_ID
from wideboy.utils.display import setup_led_matrix, render_led_matrix, blank_surface
from wideboy.utils.helpers import intro_debug
from wideboy.utils.logger import setup_logger
from wideboy.utils.pygame import (
    setup_pygame,
    process_pygame_events,
    main_entrypoint,
    run_loop,
    clock_tick,
)

from wideboy.scenes.blank import BlankScene
from wideboy.scenes.default import DefaultScene

CANVAS_SIZE = (settings.display.canvas.width, settings.display.canvas.height)

# Logging

setup_logger(level=settings.general.log_level)
logger = logging.getLogger(AppMetadata.NAME)

# Startup

intro_debug(device_id=DEVICE_ID)

# PyGame & Display

clock, screen = setup_pygame(CANVAS_SIZE)
blank_screen = blank_surface(CANVAS_SIZE)

matrix, matrix_buffer = None, None
if settings.display.matrix.enabled:
    matrix, matrix_buffer = setup_led_matrix()

# HASS

hass = setup_hass()


# Events


def process_events(events: list[pygame.event.Event]):
    global STATE, matrix
    for event in events:
        if event.type == EVENT_MQTT_MESSAGE:
            payload = json.loads(event.payload)
            logger.debug(f"event:mqtt topic={event.topic} payload={payload}")
            if event.topic.endswith("master/set"):
                HASS_MASTER.update(payload)
                logger.info(f"entity:debug entity={HASS_MASTER.state}")


# Loop Setup

running = True

# Main Loop


async def start_main_loop():

    global matrix, matrix_buffer

    loop = asyncio.get_event_loop()

    scene_manager = SceneManager(set([DefaultScene(screen), BlankScene(screen)]))
    scene_manager.run("default")

    while running:
        events = pygame.event.get()
        process_pygame_events(events)
        process_events(events)
        delta = clock_tick(clock)

        updates = scene_manager.render(delta, events)
        if len(updates):
            pygame.display.update(updates)

        if settings.display.matrix.enabled:
            matrix_buffer = render_led_matrix(
                matrix,
                screen if HASS_MASTER.state["state"] == "ON" else blank_screen,
                matrix_buffer,
                (HASS_MASTER.state["brightness"] / 255) * 100,
            )

        scene_manager.debug(clock, delta)
        await asyncio.sleep(0)


# Entrypoint

if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
