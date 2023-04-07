import asyncio
import json
import logging
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy.constants import (
    AppMetadata,
)
from wideboy.config import settings, DEVICE_ID

# from wideboy.mqtt import MQTT
from wideboy.constants import (
    DEFAULT_POWER,
    DEFAULT_BRIGHTNESS,
    EVENT_MASTER_POWER,
    EVENT_MASTER_BRIGHTNESS,
    EVENT_SCENE_MANAGER_NEXT,
)
from wideboy.mqtt.homeassistant import (
    advertise_entity,
    update_entity,
    update_sensors,
    hass_bool,
)
from wideboy.scenes.manager import SceneManager
from wideboy.utils.display import setup_led_matrix, render_led_matrix, blank_surface
from wideboy.utils.helpers import intro_debug
from wideboy.utils.logger import setup_logger
from wideboy.utils.pygame import (
    setup_pygame,
    dispatch_event,
    pump_events,
    main_entrypoint,
    run_loop,
    clock_tick,
)
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


# Home Assistant Entities
advertise_entity(
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
    dict(state="ON", brightness=128),
)
advertise_entity("scene_next", "button")
advertise_entity(
    "fps",
    "sensor",
    dict(
        device_class="frequency",
        suggested_display_precision=1,
        unit_of_measurement="fps",
        value_template="{{ value_json.value }}",
    ),
    initial_state=dict(value=0),
)
advertise_entity("action_a", "button")
advertise_entity("action_b", "button")
advertise_entity("message", "text", dict(min=1))

# Main Loop
async def start_main_loop():

    global state, matrix, matrix_buffer
    loop = asyncio.get_event_loop()

    scene_manager = SceneManager(
        [
            DefaultScene(screen),
            CreditsScene(screen),
        ]
    )

    running = True

    power = DEFAULT_POWER
    brightness = DEFAULT_BRIGHTNESS

    while running:

        # Events Processing
        pump_events()
        events = pygame.event.get()
        for event in events:
            dispatch_event(event)
            if event.type == EVENT_MASTER_POWER:
                power = event.value
                update_entity("master/state", dict(state=hass_bool(power)))
            if event.type == EVENT_MASTER_BRIGHTNESS:
                brightness = event.value
                if matrix:
                    matrix.brightness = (brightness / 255) * 100
                update_entity(
                    "master/state", dict(state=hass_bool(power), brightness=brightness)
                )
            if event.type == EVENT_SCENE_MANAGER_NEXT:
                scene_manager.next_scene()

        # Clock, Blitting, Display
        delta = clock_tick(clock)
        updates = scene_manager.render(clock, delta, events)
        pygame.display.update(updates)
        update_sensors(clock)

        if settings.display.matrix.enabled:
            matrix_buffer = render_led_matrix(
                matrix, screen if power else blank_screen, matrix_buffer
            )

        # Debugging
        scene_manager.debug(clock, delta)
        await asyncio.sleep(0)


# Entrypoint
if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
