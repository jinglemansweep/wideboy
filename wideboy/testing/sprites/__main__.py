import datetime
import enum
import logging
import pygame
import random
import time
from typing import Dict, List, Tuple

from .tiles import CustomTileGrid

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Setup

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 64


# Main Loop

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

clock = pygame.time.Clock()
FPS = 50
DEBUG = True

"""
- sensor.privacy_ip_info
- sensor.transmission_down_speed
- sensor.ds920plus_volume_used
- sensor.speedtest_download_average
- sensor.speedtest_upload_average
- sensor.speedtest_ping_average
- binary_sensor.back_door_contact_sensor_contact
- binary_sensor.front_door_contact_sensor_contact
- input_boolean.house_manual
- switch.lounge_fans
- sensor.octopus_energy_electricity_current_demand
- sensor.octopus_energy_electricity_current_rate
- sensor.octopus_energy_electricity_current_accumulative_cost
- sensor.electricity_hourly_rate
- sensor.delta_2_max_downstairs_battery_level
- sensor.delta_2_max_downstairs_cycles
- sensor.delta_2_max_downstairs_discharge_remaining_time
- sensor.delta_2_max_downstairs_charge_remaining_time
- sensor.delta_2_max_downstairs_ac_in_power
- sensor.delta_2_max_downstairs_ac_out_power
- sensor.openweathermap_wind_bearing
- sensor.openweathermap_wind_speed
- sensor.openweathermap_temperature
- sensor.openweathermap_weather_code
- sensor.hue_motion_sensor_1_temperature
- sensor.kitchen_temperature_sensor_temperature
- sensor.bedroom_temperature_sensor_temperature
- sensor.blink_garage_temperature
- sensor.blink_back_temperature
- sensor.blink_front_temperature
- sensor.blink_side_temperature
- sensor.steps_louis
- sensor.core_300s_pm2_5
"""


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


frame = 0
state: Dict = dict()
running = True


tile_grid = CustomTileGrid(state)

sprite_group: pygame.sprite.Group = pygame.sprite.Group()
sprite_group.add(tile_grid)

while running:
    now = datetime.datetime.now()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if frame % 300 == 0:
        randomise_state_common(state)
        print(f"State: {state}")
    if frame % 1000 == 0:
        randomise_state_rare(state)
        print(f"State: {state}")

    screen.fill((0, 0, 0, 255))
    sprite_group.update()
    if tile_grid.rect:
        tile_grid.rect.topleft = (SCREEN_WIDTH - tile_grid.rect.width, 0)
    sprite_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    if frame % 100 == 0:
        logger.debug(f"Frame: {frame}, FPS: {clock.get_fps()}")
    frame += 1

pygame.quit()
