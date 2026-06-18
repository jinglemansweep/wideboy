from datetime import datetime
from typing import Optional

from ...sprites.tile_grid import VerticalCollapseTileGridCell, TallGridCell
from ...sprites.tile_grid.helpers import (
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
    return f"{hours}h{minutes:01d}m"


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


def convert_kph_to_mph(kph: Optional[int] = None):
    if kph is None:
        return 0
    return round(kph * 0.621371)


def days_until(end: float):
    start = datetime.now().timestamp()
    return int(abs(int(start - end) / 60 / 60 / 24))


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

# Sensor Tiles


class CellBinCollectionBlack(GridCell):
    entity_id = "binary_sensor.bin_black"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN
    label = "Black"
    icon_color_background = CommonColors.COLOR_GREY_DARK

class CellBinCollectionBlue(GridCell):
    entity_id = "binary_sensor.bin_blue"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN
    label = "Blue"
    icon_color_background = CommonColors.COLOR_BLUE_DARK

class CellBinCollectionBrown(GridCell):
    entity_id = "binary_sensor.bin_brown"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN
    label = "Brown"
    icon_color_background = CommonColors.COLOR_GREY_DARK

class CellBinCollectionGreen(GridCell):
    entity_id = "binary_sensor.bin_green"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN
    label = "Green"
    icon_color_background = CommonColors.COLOR_GREEN_DARK

class CellBinCollectionFood(GridCell):
    entity_id = "binary_sensor.bin_food"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN
    label = "Food"
    icon_color_background = CommonColors.COLOR_GREY

class CellSensorDoorFront(GridCell):
    entity_id = "binary_sensor.front_door_contact_sensor_contact"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Front"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED


class CellSensorBackFront(GridCell):
    entity_id = "binary_sensor.back_door_contact_sensor_contact"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Back"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED


# Home Tiles

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
    limit = 80

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")


# Energy Tiles


class CellElectricityDemand(GridCell):
    entity_id = "sensor.octopus_energy_electricity_current_demand"
    icon_codepoint = FontAwesomeIcons.ICON_FA_BOLT
    limit = 1000

    @property
    def label(self):
        return format_watts(self.value)

    @property
    def open(self):
        return is_defined(self.value)

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


# Battery Tiles


class CellBatteryUpstairsLevel(GridCell):
    entity_id = "sensor.delta_2_max_upstairs_battery_level"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CHEVRON_UP
    limit = 100

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")

    @property
    def open(self):
        return is_defined(self.value) and int(self.value) < self.limit

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value < 10
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value < 10
            else CommonColors.COLOR_GREY
        )


class CellBatteryDownstairsLevel(GridCell):
    entity_id = "sensor.delta_2_max_downstairs_battery_level"
    icon_codepoint = FontAwesomeIcons.ICON_FA_CHEVRON_DOWN
    limit = 100

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")

    @property
    def open(self):
        return is_defined(self.value) and int(self.value) < self.limit

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value < 10
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value < 10
            else CommonColors.COLOR_GREY
        )


# Weather/Temp Tiles


class BaseCellTemperate(GridCell):
    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}°")


class CellWeatherTemperature(BaseCellTemperate):
    entity_id = "sensor.openweathermap_temperature"
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOUSE

    @property
    def open(self):
        return is_defined(self.value)


class CellWeatherWindSpeed(GridCell):
    entity_id = "sensor.openweathermap_wind_speed"
    icon_codepoint = FontAwesomeIcons.ICON_FA_WIND

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}m/s")

    @property
    def open(self):
        return is_defined(self.value)


class CellWeatherRainProbability(GridCell):
    entity_id = "sensor.openweathermap_rain"
    icon_codepoint = FontAwesomeIcons.ICON_FA_UMBRELLA

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}mm")

    @property
    def open(self):
        return is_defined(self.value)


# Date/Time Tiles


class CellDateDogsFleaTreatment(GridCell):
    entity_id = "input_datetime.dogs_flea_treatment"
    icon_codepoint = FontAwesomeIcons.ICON_FA_BUG

    @property
    def open(self):
        days = days_until(float(self.entity_state.get("timestamp", 0)))
        return days < 7

    @property
    def label(self):
        if "day" not in self.entity_state or "month" not in self.entity_state:
            return "N/A"
        return f"{self.entity_state['day']}/{self.entity_state['month']}"


class CellDateDogsWormTreatment(GridCell):
    entity_id = "input_datetime.dogs_worm_treatment"
    icon_codepoint = FontAwesomeIcons.ICON_FA_WORM

    @property
    def open(self):
        days = days_until(float(self.entity_state.get("timestamp", 0)))
        return days < 14

    @property
    def label(self):
        if "day" not in self.entity_state or "month" not in self.entity_state:
            return "N/A"
        return f"{self.entity_state['day']}/{self.entity_state['month']}"


# Tall Cells


class TestTallCell(TallGridCell):
    pass


CELLS = [
    # [TestTallCell],
    [
        CellBinCollectionBlack,
        CellBinCollectionBlue,
        CellBinCollectionBrown,
        CellBinCollectionGreen,
        CellBinCollectionFood
    ],
    [
        CellDateDogsFleaTreatment,
        CellDateDogsWormTreatment,
        CellSensorDoorFront,
        CellSensorBackFront,
    ],
    [
        CellDS920VolumeUsage,
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        CellSpeedTestPing,
    ],
    #[
    #    CellBatteryUpstairsLevel,
    #    CellBatteryDownstairsLevel,
    #    CellSolarTotalWatts,
    #],
    [
         CellElectricityDemand
    #    CellElectricityRate,
    #    CellElectricityAccumulativeCost,
    ],
    [
        CellWeatherTemperature,
        CellWeatherWindSpeed,
        CellWeatherRainProbability,
    ],
]
