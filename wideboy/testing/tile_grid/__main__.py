import datetime
import enum
import logging
import pygame
import random
import time
from typing import Dict, List, Tuple

from wideboy.scenes.base import BaseScene
from wideboy.constants import EVENT_HASS_STATESTREAM_UPDATE
from .tiles import (
    CustomTileGrid,
    CellSpeedTestDownload,
    CellSpeedTestUpload,
    CellSpeedTestPing,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Helper Functions


def randomise_state_common(state: Dict):
    electricity_current_demand = random.randint(0, 3000)
    state.update(
        {
            "sensor.octopus_energy_electricity_current_demand": electricity_current_demand,
        }
    )


def randomise_state_rare(state: Dict):
    electricity_current_rate = random.randint(0, 100) / 100
    electricity_current_accumulative_cost = random.randint(0, 100) / 100
    speedtest_download = random.randint(0, 1000)
    speedtest_upload = random.randint(0, 1000)
    speedtest_ping = random.randint(0, 100)
    ds920plus_volume_used = random.randint(0, 100)
    state.update(
        {
            "sensor.delta_2_max_downstairs_battery_level": random.randint(0, 100),
            "sensor.delta_2_max_downstairs_ac_in_power": random.randint(0, 1000),
            "sensor.delta_2_max_downstairs_ac_out_power": random.randint(0, 1000),
            "sensor.octopus_energy_electricity_current_rate": electricity_current_rate,
            "sensor.octopus_energy_electricity_current_rate": electricity_current_accumulative_cost,
            "sensor.speedtest_download_average": speedtest_download,
            "sensor.speedtest_upload_average": speedtest_upload,
            "sensor.speedtest_ping_average": speedtest_ping,
            "sensor.ds920plus_volume_used": ds920plus_volume_used,
            "switch.lounge_fans": "on" if random.choice([True, False]) else "off",
        }
    )


# Setup

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 64

FPS = 50
DEBUG = True

CELLS = [
    [CellSpeedTestDownload],
    [CellSpeedTestUpload],
    [CellSpeedTestPing],
    [CellSpeedTestUpload, CellSpeedTestPing],
]

# Main Loop

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

clock = pygame.time.Clock()


frame = 0
state: Dict = dict()
running = True


class MockEngine:
    state: Dict

    def __init__(self, state):
        self.state = state


class MockScene:
    def __init__(self, state: Dict):
        self.engine = MockEngine(state)


rect = pygame.Rect(0, 0, 256, 64)


scene = MockScene(state)
tile_grid = CustomTileGrid(scene, CELLS)  # type: ignore


group: pygame.sprite.Group = pygame.sprite.Group()
group.add(tile_grid)


while running:
    now = datetime.datetime.now()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if frame % 50 == 0:
        randomise_state_common(state)
        print(f"State: {state}")
    if frame % 200 == 0:
        randomise_state_rare(state)
        print(f"State: {state}")

    screen.fill(pygame.Color(0, 0, 0, 255))
    group.update(frame, clock, 0, [pygame.event.Event(EVENT_HASS_STATESTREAM_UPDATE)])
    group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    if frame % 100 == 0:
        logger.debug(f"Frame: {frame}, FPS: {clock.get_fps()}")
    frame += 1

pygame.quit()
