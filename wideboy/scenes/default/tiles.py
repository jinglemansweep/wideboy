import datetime
import enum
import pygame
import random

from typing import Optional

from wideboy.sprites.tile_grid import VerticalCollapseTileGridCell, TileGrid
from wideboy.sprites.tile_grid.helpers import (
    CommonColors,
    FontAwesomeIcons,
    is_defined,
    template_if_defined,
)

# CUSTOM SUBCLASSES


class GridCell(VerticalCollapseTileGridCell):
    cell_color_background = CommonColors.COLOR_GREY_DARK
    icon_color_background = CommonColors.COLOR_GREY


# CUSTOM FUNCTIONS


def format_watts(watts: Optional[int] = None):
    if watts is None:
        return "N/A"
    return "{:.0f}W".format(watts) if watts < 1000 else "{:.1f}kW".format(watts / 1000)


def format_minutes(minutes: Optional[int] = None):
    if minutes is None:
        return "N/A"
    hours = int(minutes) // 60
    minutes = int(minutes) % 60
    return f"{hours}h{minutes:02d}m"


def format_compass_bearing(bearing: Optional[int] = None):
    if bearing is None:
        return "N/A"
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][
        int(((bearing + 22.5) % 360) / 45)
    ]


def convert_ms_to_mph(ms: Optional[int] = None):
    if ms is None:
        return 0
    return round(ms * 2.237)


# CUSTOM COLUMNS

rainbox_colors = [
    CommonColors.COLOR_RED,
    CommonColors.COLOR_ORANGE,
    CommonColors.COLOR_YELLOW,
    CommonColors.COLOR_GREEN,
    CommonColors.COLOR_BLUE,
    CommonColors.COLOR_PURPLE,
    CommonColors.COLOR_PINK,
]

# CONSTANTS

HOUR_EVENING = 20

# TILE DEFINITIONS

# Switch Tiles


class CellSwitchBooleanManual(GridCell):
    entity_id = "input_boolean.house_manual"
    label = "Manual"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TOGGLE_OFF

    @property
    def open(self):
        return self.value == True


class CellSwitchLoungeFan(GridCell):
    entity_id = "switch.lounge_fans"
    label = "Fan"
    icon_codepoint = FontAwesomeIcons.ICON_FA_FAN

    @property
    def open(self):
        return self.value == True


# Sensor Tiles


class CellSensorStepsLouis(GridCell):
    entity_id = "sensor.steps_louis"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PERSON_WALKING

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}")

    @property
    def open(self):
        return is_defined(self.value) and self.value > 500


class CellSensorLoungeAirPM(GridCell):
    entity_id = "sensor.core_300s_pm2_5"
    icon_codepoint = FontAwesomeIcons.ICON_FA_SMOKING

    @property
    def value_quality(self):
        return self.state.get("sensor.core_300s_air_quality")

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}")

    @property
    def open(self):
        return is_defined(self.value_quality) and self.value_quality > 2

    @property
    def cell_color_background(self):
        if self.value_quality == 1:
            return CommonColors.COLOR_BLUE_DARK
        elif self.value_quality == 2:
            return CommonColors.COLOR_GREEN_DARK
        elif self.value_quality == 3:
            return CommonColors.COLOR_ORANGE_DARK
        else:
            return CommonColors.COLOR_RED_DARK

    @property
    def icon_color_background(self):
        if self.value_quality == 1:
            return CommonColors.COLOR_BLUE
        elif self.value_quality == 2:
            return CommonColors.COLOR_GREEN
        elif self.value_quality == 3:
            return CommonColors.COLOR_ORANGE
        else:
            return CommonColors.COLOR_RED


class CellSensorDoorFront(GridCell):
    entity_id = "binary_sensor.front_door_contact_sensor_contact"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Front"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED

    @property
    def open(self):
        return self.value


class CellSensorBackFront(GridCell):
    entity_id = "binary_sensor.back_door_contact_sensor_contact"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Back"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED

    @property
    def open(self):
        return self.value


# Home Lab Tiles


class CellSpeedTestDownload(GridCell):
    entity_id = "sensor.speedtest_download_average"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_DOWN
    limit = 500

    @property
    def open(self):
        return is_defined(self.value) and self.value < self.limit

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}Mb")


class CellSpeedTestUpload(GridCell):
    entity_id = "sensor.speedtest_upload_average"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_UP
    limit = 500

    @property
    def open(self):
        return is_defined(self.value) and self.value < self.limit

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}Mb")


class CellSpeedTestPing(GridCell):
    entity_id = "sensor.speedtest_ping_average"
    icon_codepoint = FontAwesomeIcons.ICON_FA_HEART_PULSE
    limit = 10

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}ms")


class CellDS920VolumeUsage(GridCell):
    entity_id = "sensor.ds920plus_volume_used"
    icon_codepoint = FontAwesomeIcons.ICON_FA_HARD_DRIVE
    limit = 70

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")


# Motion Tiles


class CellMotionFrontDoor(GridCell):
    entity_id = "binary_sensor.front_door_motion"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED

    @property
    def open(self):
        return self.value

    @property
    def label(self):
        return f"Front"


class CellMotionFrontGarden(GridCell):
    entity_id = "binary_sensor.blink_front_motion_detected"
    icon_codepoint = FontAwesomeIcons.ICON_FA_ROAD

    @property
    def open(self):
        return self.value

    @property
    def label(self):
        return f"Front"


class CellMotionBackGarden(GridCell):
    entity_id = "binary_sensor.blink_back_motion_detected"
    icon_codepoint = FontAwesomeIcons.ICON_FA_LEAF

    @property
    def open(self):
        return self.value

    @property
    def label(self):
        return f"Back"


class CellMotionHouseSide(GridCell):
    entity_id = "binary_sensor.blink_side_motion_detected"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CAR

    @property
    def open(self):
        return self.value

    @property
    def label(self):
        return f"Side"


class CellMotionGarage(GridCell):
    entity_id = "binary_sensor.blink_side_motion_detected"
    icon_codepoint = FontAwesomeIcons.ICON_FA_WAREHOUSE

    @property
    def open(self):
        return self.value

    @property
    def label(self):
        return f"Garage"


# Temperature Tiles


class BaseCellTemperate(GridCell):
    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}°")


class CellTemperatureLounge(BaseCellTemperate):
    entity_id = "sensor.lounge_temperature_sensor_temperature"
    icon_codepoint = FontAwesomeIcons.ICON_FA_COUCH
    limit_min = 20
    limit_max = 28

    @property
    def open(self):
        return is_defined(self.value) and (
            self.value < self.limit_min or self.value > self.limit_max
        )


class CellTemperatureBedroom(BaseCellTemperate):
    entity_id = "sensor.bedroom_temperature_sensor_temperature"
    icon_codepoint = FontAwesomeIcons.ICON_FA_BED
    limit_min = 20
    limit_max = 28

    @property
    def open(self):
        return is_defined(self.value) and (
            self.value < self.limit_min or self.value > self.limit_max
        )


# Energy Tiles


class CellElectricityDemand(GridCell):
    entity_id = "sensor.octopus_energy_electricity_current_demand"
    icon_codepoint = FontAwesomeIcons.ICON_FA_BOLT
    limit = 600

    @property
    def label(self):
        return format_watts(self.value)

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY
        )


class CellElectricityRate(GridCell):
    entity_id = "sensor.octopus_energy_electricity_current_rate"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_HALF_STROKE

    @property
    def label(self):
        return template_if_defined(self.value, "£{:.2f}")

    @property
    def cell_color_background(self):
        if self.value is None:
            return CommonColors.COLOR_GREY_DARK
        elif self.value < 0.00:
            return CommonColors.COLOR_BLUE_DARK
        elif self.value <= 0.20:
            return CommonColors.COLOR_GREEN_DARK
        elif self.value <= 0.30:
            return CommonColors.COLOR_ORANGE_DARK
        else:
            return CommonColors.COLOR_RED_DARK

    @property
    def icon_color_background(self):
        if self.value is None:
            return CommonColors.COLOR_GREY
        if self.value < 0.00:
            return CommonColors.COLOR_BLUE
        elif self.value <= 0.20:
            return CommonColors.COLOR_GREEN
        elif self.value <= 0.30:
            return CommonColors.COLOR_ORANGE
        else:
            return CommonColors.COLOR_RED


class CellElectricityAccumulativeCost(GridCell):
    entity_id = "sensor.octopus_energy_electricity_current_accumulative_cost"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG
    limit = 3.00

    @property
    def label(self):
        return template_if_defined(self.value, "£{:.2f}")

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY
        )


class CellGasAccumulativeCost(GridCell):
    entity_id = "sensor.octopus_energy_gas_current_accumulative_cost"
    icon_codepoint = FontAwesomeIcons.ICON_FA_FIRE_FLAME_SIMPLE
    limit = 3.00

    @property
    def label(self):
        return template_if_defined(self.value, "£{:.2f}")

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY
        )


class CellBatteryLevel(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_battery_level"
    limit = 30

    @property
    def label(self):
        return template_if_defined(self.value, "{}%")

    @property
    def open(self):
        return is_defined(self.value) and self.value < 50

    @property
    def icon_codepoint(self):
        if self.value is None:
            return None
        if self.value < 20:
            return FontAwesomeIcons.ICON_FA_BATTERY_EMPTY
        elif self.value < 40:
            return FontAwesomeIcons.ICON_FA_BATTERY_QUARTER
        elif self.value < 60:
            return FontAwesomeIcons.ICON_FA_BATTERY_HALF
        elif self.value < 80:
            return FontAwesomeIcons.ICON_FA_BATTERY_THREE_QUARTERS
        else:
            return FontAwesomeIcons.ICON_FA_BATTERY_FULL

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value > self.limit
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value < self.limit
            else CommonColors.COLOR_GREY
        )


class CellBatteryACInput(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_ac_in_power"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_PLUS

    @property
    def open(self):
        return is_defined(self.value) and self.value > 0

    @property
    def label(self):
        return format_watts(self.value)


class CellBatteryACOutput(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_ac_out_power"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_MINUS

    @property
    def open(self):
        return is_defined(self.value) and self.value > 0

    @property
    def label(self):
        return format_watts(self.value)


class CellBatteryChargeRemainingTime(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_charge_remaining_time"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_PLUS
    icon_color_background = CommonColors.COLOR_GREEN_DARK

    @property
    def open(self):
        return is_defined(self.value) and self.value > 0

    @property
    def label(self):
        return format_minutes(self.value)


class CellBatteryDischargeRemainingTime(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_discharge_remaining_time"
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_MINUS
    icon_color_background = CommonColors.COLOR_RED_DARK

    @property
    def open(self):
        return is_defined(self.value) and self.value > 0

    @property
    def label(self):
        return format_minutes(self.value)


# Weather Tiles


class CellWeatherTemperature(BaseCellTemperate):
    entity_id = "sensor.openweathermap_temperature"
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOUSE


class CellWeatherWindSpeed(GridCell):
    entity_id = "sensor.openweathermap_wind_speed"
    icon_codepoint = FontAwesomeIcons.ICON_FA_WIND

    @property
    def label(self):
        return f"{convert_ms_to_mph(self.value)}mph"

    @property
    def open(self):
        return is_defined(self.value) and self.value > 5


class CellWeatherRainProbability(GridCell):
    entity_id = "sensor.openweathermap_forecast_precipitation_probability"
    icon_codepoint = FontAwesomeIcons.ICON_FA_UMBRELLA

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")

    @property
    def open(self):
        return is_defined(self.value) and self.value > 0


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
