import asyncio
import json
import logging
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy.constants import (
    AppMetadata,
    EVENT_MASTER_POWER,
    EVENT_MASTER_BRIGHTNESS,
    EVENT_SCENE_NEXT,
)
from wideboy.config import (
    settings,
)
from wideboy.mqtt import MQTT
from wideboy.mqtt.homeassistant import (
    setup_hass,
    advertise_entity,
    process_hass_mqtt_events,
)
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
from wideboy.scenes.credits import CreditsScene
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

# Home Assistant

hass = setup_hass()

advertise_entity(
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
    dict(state="ON", brightness=128),
)

advertise_entity("scene_next", "button")

# Main Loop


async def start_main_loop():

    global state, matrix, matrix_buffer

    loop = asyncio.get_event_loop()

    scene_manager = SceneManager(
        [CreditsScene(screen), DefaultScene(screen), BlankScene(screen)]
    )
    scene_manager.change_scene("credits")

    running = True

    while running:

        # Events Processing

        events = pygame.event.get()
        process_pygame_events(events)
        process_hass_mqtt_events(events)
        for event in events:
            if event.type == EVENT_MASTER_POWER:
                STATE.power = event.value
                MQTT.publish(
                    "master/state",
                    dict(
                        state="ON" if STATE.power else "OFF",
                        brightness=STATE.brightness,
                    ),
                )
            if event.type == EVENT_MASTER_BRIGHTNESS:
                STATE.brightness = event.value
                if matrix:
                    matrix.brightness = (STATE.brightness / 255) * 100
                MQTT.publish(
                    "master/state",
                    dict(
                        state="ON" if STATE.power else "OFF",
                        brightness=STATE.brightness,
                    ),
                )
            if event.type == EVENT_SCENE_NEXT:
                scene_manager.next_scene()

        # Clock, Blitting, Display

        delta = clock_tick(clock)
        updates = scene_manager.render(delta, events)
        pygame.display.update(updates)

        if settings.display.matrix.enabled:
            matrix_buffer = render_led_matrix(
                matrix, screen if STATE.power else blank_screen, matrix_buffer
            )

        # Debugging

        scene_manager.debug(clock, delta)
        await asyncio.sleep(0)


# Entrypoint

if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
