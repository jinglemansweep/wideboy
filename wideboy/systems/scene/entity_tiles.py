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


class CellSensorBinCollection(GridCell):
    entity_id = "calendar.bin_collection"
    icon_codepoint = FontAwesomeIcons.ICON_FA_TRASH_CAN

    @property
    def bin_type(self):
        return self.entity_state.get("message", "")[1:-1].lower()

    @property
    def label(self):
        return f"{self.bin_type.capitalize()}"

    @property
    def open(self):
        return self.value is True

    @property
    def cell_color_background(self):
        if self.bin_type == "blue":
            return CommonColors.COLOR_BLUE_DARK
        else:
            return CommonColors.COLOR_GREY_DARK

    @property
    def icon_color_background(self):
        if self.bin_type == "blue":
            return CommonColors.COLOR_BLUE
        else:
            return CommonColors.COLOR_GREY


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
        try:
            return int(
                self.state.get("sensor.core_300s_air_quality", dict()).get("state", 0)
            )
        except ValueError:
            return None

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}")

    @property
    def open(self):
        return is_defined(self.value_quality) and self.value_quality > 3

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


class CellSensorBackFront(GridCell):
    entity_id = "binary_sensor.back_door_contact_sensor_contact"
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Back"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED


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


class CellVPNPrivacyStatus(GridCell):
    entity_id = "binary_sensor.vpn_privacy_status"
    icon_codepoint = FontAwesomeIcons.ICON_FA_SHIELD_HALVED
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED

    @property
    def open(self):
        return is_defined(self.value) and not self.value

    @property
    def label(self):
        return "VPN"


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
    limit = 2.00
    limit_high = 3.00

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
            if is_defined(self.value) and self.value > self.limit_high
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value > self.limit_high
            else CommonColors.COLOR_GREY
        )


class CellBatteryUpstairs(GridCell):
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
            if is_defined(self.value) and self.value < 30
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value < 30
            else CommonColors.COLOR_GREY
        )


class CellBatteryDownstairs(GridCell):
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
            if is_defined(self.value) and self.value < 30
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value < 30
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


class CellWeatherWindSpeed(GridCell):
    entity_id = "sensor.openweathermap_wind_speed"
    icon_codepoint = FontAwesomeIcons.ICON_FA_WIND
    limit = 10.0

    @property
    def label(self):
        return f"{convert_ms_to_mph(self.value)}mph"

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit


class CellWeatherRainProbability(GridCell):
    entity_id = "sensor.openweathermap_forecast_precipitation_probability"
    icon_codepoint = FontAwesomeIcons.ICON_FA_UMBRELLA
    limit = 30.0

    @property
    def label(self):
        return template_if_defined(self.value, "{:.0f}%")

    @property
    def open(self):
        return is_defined(self.value) and self.value > self.limit


class CellHouseUpstairsRackTemperature(BaseCellTemperate):
    entity_id = "sensor.laundry_temperature_sensor_temperature"
    icon_codepoint = FontAwesomeIcons.ICON_FA_SERVER
    limit_high = 40

    @property
    def open(self):
        return is_defined(self.value) and int(self.value)

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if is_defined(self.value) and self.value > self.limit_high
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if is_defined(self.value) and self.value > self.limit_high
            else CommonColors.COLOR_GREY
        )


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
        CellSensorBinCollection,
        CellSensorStepsLouis,
        CellSensorLoungeAirPM,
        CellSensorDoorFront,
        CellSensorBackFront,
    ],
    [
        CellVPNPrivacyStatus,
        CellDS920VolumeUsage,
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        CellSpeedTestPing,
    ],
    [
        CellElectricityDemand,
        CellElectricityRate,
        CellElectricityAccumulativeCost,
        CellBatteryUpstairs,
        CellBatteryDownstairs,
    ],
    [
        CellWeatherTemperature,
        CellWeatherWindSpeed,
        CellWeatherRainProbability,
        CellHouseUpstairsRackTemperature,
        CellDateDogsFleaTreatment,
        CellDateDogsWormTreatment,
    ],
]
