import datetime
import enum
import logging
import pygame
import random
import time
from typing import Dict, List, Tuple

from wideboy.scenes.base import BaseScene
from wideboy.constants import EVENT_HASS_STATESTREAM_UPDATE
from wideboy.sprites.tile_grid import TileGrid
from wideboy.scenes.default.tiles import (
    CellSensorStepsLouis,
    CellSensorLoungeAirPM,
    CellSensorDoorFront,
    CellSensorBackFront,
    CellSwitchLoungeFan,
    CellSwitchBooleanManual,
    # --
    CellMotionFrontDoor,
    CellMotionFrontGarden,
    CellMotionBackGarden,
    CellMotionHouseSide,
    CellMotionGarage,
    # --
    CellDS920VolumeUsage,
    CellSpeedTestDownload,
    CellSpeedTestUpload,
    CellSpeedTestPing,
    # --
    CellElectricityDemand,
    CellElectricityRate,
    CellElectricityAccumulativeCost,
    CellGasAccumulativeCost,
    CellBatteryLevel,
    CellBatteryDischargeRemainingTime,
    # --
    CellWeatherTemperature,
    CellWeatherWindSpeed,
    CellWeatherRainProbability,
    CellTemperatureLounge,
    CellTemperatureBedroom,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Helper Functions


def randomise_state_common(state: Dict):
    state.update(
        {
            "sensor.octopus_energy_electricity_current_demand": random.randint(0, 3000),
        }
    )


def randomise_state_rare(state: Dict):
    state.update(
        {
            "binary_sensor.blink_front_motion_detected": random.choice([True, False]),
            "binary_sensor.blink_back_motion_detected": random.choice([True, False]),
            "binary_sensor.blink_side_motion_detected": random.choice([True, False]),
            "binary_sensor.blink_side_motion_detected": random.choice([True, False]),
            "binary_sensor.front_door_contact_sensor_contact": random.choice(
                [True, False]
            ),
            "binary_sensor.front_door_motion": random.choice([True, False]),
            "binary_sensor.back_door_contact_sensor_contact": random.choice(
                [True, False]
            ),
            "sensor.bedroom_temperature_sensor_temperature": random.randint(10, 30),
            "sensor.delta_2_max_downstairs_battery_level": random.randint(0, 100),
            "sensor.delta_2_max_downstairs_ac_in_power": random.randint(0, 1000),
            "sensor.delta_2_max_downstairs_ac_out_power": random.randint(0, 1000),
            "sensor.delta_2_max_downstairs_charge_remaining_time": random.randint(
                0, 60 * 5
            ),
            "sensor.delta_2_max_downstairs_discharge_remaining_time": random.randint(
                0, 60 * 5
            ),
            "sensor.hue_motion_sensor_1_temperature": random.randint(10, 30),
            "sensor.octopus_energy_electricity_current_rate": random.randint(0, 100)
            / 100,
            "sensor.octopus_energy_electricity_current_accumulative_cost": random.randint(
                0, 100
            )
            / 100,
            "sensor.octopus_energy_gas_current_accumulative_cost": random.randint(
                0, 100
            )
            / 100,
            "sensor.core_300s_pm2_5": random.randint(0, 300),
            "sensor.core_300s_air_quality": random.randint(1, 4),
            "sensor.speedtest_download_average": random.randint(0, 1000),
            "sensor.speedtest_upload_average": random.randint(0, 1000),
            "sensor.speedtest_ping_average": random.randint(0, 100),
            "sensor.ds920plus_volume_used": random.randint(0, 100),
            "sensor.openweathermap_temperature": random.randint(1, 30),
            "sensor.openweathermap_wind_speed": random.randint(0, 60),
            "sensor.openweathermap_forecast_precipitation_probability": random.randint(
                0, 100
            ),
            "sensor.steps_louis": random.randint(0, 5000),
            "switch.lounge_fans": random.choice([True, False]),
            "input_boolean.house_manual": random.choice([True, False]),
        }
    )


# Setup

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 64

FPS = 50
DEBUG = True

CELLS = [
    [
        CellSensorStepsLouis,
        CellSensorLoungeAirPM,
        CellSensorDoorFront,
        CellSensorBackFront,
        CellSwitchLoungeFan,
        CellSwitchBooleanManual,
    ],
    [
        CellMotionFrontDoor,
        CellMotionFrontGarden,
        CellMotionBackGarden,
        CellMotionHouseSide,
        CellMotionGarage,
    ],
    [
        CellDS920VolumeUsage,
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        CellSpeedTestPing,
    ],
    [
        CellElectricityDemand,
        CellElectricityRate,
        CellElectricityAccumulativeCost,
        CellGasAccumulativeCost,
        CellBatteryLevel,
        CellBatteryDischargeRemainingTime,
    ],
    [
        CellWeatherTemperature,
        CellWeatherWindSpeed,
        CellWeatherRainProbability,
        CellTemperatureLounge,
        CellTemperatureBedroom,
    ],
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
tile_grid = TileGrid(scene, CELLS)  # type: ignore


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
    group.update(
        frame,
        clock,
        0,
        [pygame.event.Event(EVENT_HASS_STATESTREAM_UPDATE, dict(payload=dict()))],
    )
    group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    if frame % 100 == 0:
        logger.debug(f"Frame: {frame}, FPS: {clock.get_fps()}")
    frame += 1

pygame.quit()
