import asyncio
import logging
import os
import pygame
import pygame.pkgdata
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy import _APP_NAME
from wideboy.config import LOG_DEBUG, CANVAS_SIZE, MATRIX_ENABLED
from wideboy.utils.display import setup_led_matrix, render_led_matrix, blank_surface
from wideboy.utils.helpers import intro_debug
from wideboy.utils.logger import setup_logger
from wideboy.utils.hass import setup_hass, configure_entity, EVENT_HASS_COMMAND
from wideboy.utils.mqtt import setup_mqtt
from wideboy.utils.tasks import fetch_weather
from wideboy.utils.pygame import (
    setup_pygame,
    process_pygame_events,
    main_entrypoint,
    run_loop,
    loop_debug,
    clock_tick,
)
from wideboy.utils.state import state
from wideboy.utils.scenes import SceneManager
from wideboy.scenes.blank import BlankScene
from wideboy.scenes.default import DefaultScene

# Logging

setup_logger(debug=LOG_DEBUG)
logger = logging.getLogger(_APP_NAME)

# Startup

intro_debug()

# PyGame & Display

clock, screen = setup_pygame(CANVAS_SIZE)
blank_screen = blank_surface(CANVAS_SIZE)
if MATRIX_ENABLED:
    matrix, matrix_buffer = setup_led_matrix()

# MQTT

mqtt = setup_mqtt()

# HASS

hass = setup_hass()

switch_power_state_topic = configure_entity(
    mqtt,
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
)
mqtt.publish(switch_power_state_topic, {"state": "ON", "brightness": 128})

# Events


def process_events(events: list[pygame.event.Event]):
    global state, matrix
    for event in events:
        if event.type == EVENT_HASS_COMMAND:
            logger.debug(f"hass:action name={event.name} payload={event.payload}")
            if event.name == "master":
                state.power = event.payload.get("state") == "ON"
                if "brightness" in event.payload:
                    state.brightness = int(event.payload.get("brightness"))
                    matrix.brightness = (state.brightness / 255) * 100
                mqtt.publish(switch_power_state_topic, event.payload)
                logger.info(f"power:master state={event.payload}")


# Loop Setup

running = True

# Main Loop


async def start_main_loop():

    global state, matrix, matrix_buffer

    loop = asyncio.get_event_loop()

    asyncio.create_task(fetch_weather(loop, state))

    scene_manager = SceneManager()
    scene_manager.add(DefaultScene(screen, state))
    scene_manager.add(BlankScene(screen, state))

    while running:
        events = pygame.event.get()
        process_pygame_events(events)
        process_events(events)
        delta = clock_tick(clock)

        updates = scene_manager.render(delta, events)
        if len(updates):
            # logger.debug(f"display:draw rects={len(updates)}")
            pygame.display.update(updates)

        # if scene_manager.frame % 1000 == 0:
        #    scene_manager.next()

        if MATRIX_ENABLED:
            matrix_buffer = render_led_matrix(
                matrix, screen if state.power else blank_screen, matrix_buffer
            )

        scene_manager.debug(clock, delta, state)
        mqtt.loop(0.003)
        await asyncio.sleep(0)


# Entrypoint

if __name__ == "__main__":
    main_entrypoint(run_loop(start_main_loop))
