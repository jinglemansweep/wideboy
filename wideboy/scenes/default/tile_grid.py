import datetime
import enum
import pygame
import random

from wideboy.sprites.tile_grid import (
    TileGrid,
    HorizontalCollapseTileGridColumn,
    VerticalCollapseTileGridCell,
    CommonColors,
    FontAwesomeIcons,
)


# CUSTOM SUBCLASSES


class GridCell(VerticalCollapseTileGridCell):
    cell_color_background = CommonColors.COLOR_GREY_DARK
    icon_color_background = CommonColors.COLOR_GREY


# CUSTOM FUNCTIONS


def format_watts(watts: int):
    return "{:.0f}W".format(watts) if watts < 1000 else "{:.1f}kW".format(watts / 1000)

def format_minutes(minutes: int):
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}:{minutes:02d}"

# TILE DEFINITIONS

# Electricity Tiles


class CellElectricityDemand(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BOLT
    limit_high = 500

    @property
    def value(self):
        return float(
            self.state.get("sensor.octopus_energy_electricity_current_demand", 0)
        )

    @property
    def label(self):
        return format_watts(self.value)

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY
        )


class CellElectricityRate(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOURGLASS
    limit_high = 0.30

    @property
    def value(self):
        return float(
            self.state.get("sensor.octopus_energy_electricity_current_rate", 0)
        )

    @property
    def label(self):
        return f"£{self.value:.2f}"

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY
        )


class CellElectricityAccumulativeCost(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CLOCK

    @property
    def value(self):
        return float(
            self.state.get(
                "sensor.octopus_energy_electricity_current_accumulative_cost", 0
            )
        )

    @property
    def label(self):
        return f"£{self.value:.2f}"


# Battery Tiles


class CellBatteryLevel(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BATTERY_FULL

    @property
    def value(self):
        return int(self.state.get("sensor.delta_2_max_downstairs_battery_level", 0))

    @property
    def label(self):
        return f"{self.value}%"


class CellBatteryACInput(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_PLUS

    @property
    def value(self):
        return int(self.state.get("sensor.delta_2_max_downstairs_ac_in_power", 0))

    @property
    def open(self):
        return self.value > 100

    @property
    def label(self):
        return format_watts(self.value)


class CellBatteryACOutput(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_MINUS

    @property
    def value(self):
        return int(self.state.get("sensor.delta_2_max_downstairs_ac_out_power", 0))

    @property
    def open(self):
        return self.value > 100

    @property
    def label(self):
        return format_watts(self.value)

class CellBatteryChargeRemainingTime(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_PLUS
    icon_color_background = CommonColors.COLOR_GREEN_DARK

    @property
    def value(self):
        return int(self.state.get("sensor.delta_2_max_downstairs_charge_remaining_time", 0))

    @property
    def open(self):
        return self.value > 0

    @property
    def label(self):
        return format_minutes(self.value)

class CellBatteryDischargeRemainingTime(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_MINUS
    icon_color_background = CommonColors.COLOR_RED_DARK

    @property
    def value(self):
        return int(self.state.get("sensor.delta_2_max_downstairs_discharge_remaining_time", 0))

    @property
    def open(self):
        return self.value > 0

    @property
    def label(self):
        return format_minutes(self.value)

# Network Tiles


class CellSpeedTestDownload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_DOWN
    limit_low = 500

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_download_average", 0))

    @property
    def open(self):
        return self.value < self.limit_low

    @property
    def label(self):
        return f"{self.value}Mb"


class CellSpeedTestUpload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_UP
    limit_low = 500

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_upload_average", 0))

    @property
    def open(self):
        return self.value < self.limit_low

    @property
    def label(self):
        return f"{self.value}Mb"


class CellSpeedTestPing(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HEART_PULSE
    limit_high = 10

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_ping_average", 0))

    @property
    def open(self):
        return self.value > self.limit_high

    @property
    def label(self):
        return f"{self.value}ms"


class CellDS920VolumeUsage(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HARD_DRIVE
    limit_high = 70

    @property
    def value(self):
        return int(self.state.get("sensor.ds920plus_volume_used", 0))

    @property
    def open(self):
        return self.value > self.limit_high

    @property
    def label(self):
        return f"{self.value}%"


# Temperature Tiles


class CellTemperatureOutside(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOUSE

    @property
    def value(self):
        return float(self.state.get("sensor.openweathermap_temperature", 0))

    @property
    def label(self):
        return f"{self.value:.1f}°"


class CellTemperatureLounge(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_COUCH

    @property
    def value(self):
        return float(self.state.get("sensor.hue_motion_sensor_1_temperature", 0))

    @property
    def label(self):
        return f"{self.value:.1f}°"


class CellTemperatureBedroom(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BED

    @property
    def value(self):
        return float(self.state.get("sensor.bedroom_temperature_sensor_temperature", 0))

    @property
    def label(self):
        return f"{self.value:.1f}°"


class CellTemperatureKitchen(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_SINK

    @property
    def value(self):
        return float(self.state.get("sensor.kitchen_temperature_sensor_temperature", 0))

    @property
    def label(self):
        return f"{self.value:.1f}°"


# Test Tiles


class CellTestRandom(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_DICE_THREE

    @property
    def value(self):
        return datetime.datetime.now().second

    @property
    def open(self):
        return self.value < 45

    @property
    def label(self):
        return f"{self.value}"


# Sensor Tiles


class CellSensorStepsLouis(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PERSON_WALKING

    @property
    def value(self):
        return int(self.state.get("sensor.steps_louis", 0))

    @property
    def label(self):
        return f"{self.value}"


class CellSensorLoungeAirPM(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_WIND
    limit_high = 50

    @property
    def value(self):
        return int(self.state.get("sensor.core_300s_pm2_5", 0))

    @property
    def label(self):
        return f"{self.value}"

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return (
            CommonColors.COLOR_RED
            if self.value > self.limit_high
            else CommonColors.COLOR_GREY
        )


class CellSensorDoorFront(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Front"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED

    @property
    def value(self):
        return self.state.get("binary_sensor.front_door_contact_sensor_contact", False)

    @property
    def open(self):
        return self.value


class CellSensorBackFront(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_DOOR_CLOSED
    label = "Back"
    cell_color_background = CommonColors.COLOR_RED_DARK
    icon_color_background = CommonColors.COLOR_RED

    @property
    def value(self):
        return self.state.get("binary_sensor.back_door_contact_sensor_contact", False)

    @property
    def open(self):
        return self.value


# Switch Tiles


class CellSwitchLoungeFan(GridCell):
    label = "Fan"
    icon_codepoint = FontAwesomeIcons.ICON_FA_FAN

    @property
    def value(self):
        return self.state.get("switch.lounge_fans", False)

    @property
    def open(self):
        return self.value == True


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


class GridColumnSwitches(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[1]
    cells = [CellSwitchLoungeFan]


class GridColumnSensors(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[0]
    cells = [
        CellSensorStepsLouis,
        CellSensorLoungeAirPM,
        CellSensorDoorFront,
        CellSensorBackFront,
    ]


class GridColumnHomeLab(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[1]
    cells = [
        CellDS920VolumeUsage,
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        CellSpeedTestPing,
    ]


class GridColumnTemperature(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[2]
    cells = [
        CellTemperatureOutside,
        CellTemperatureLounge,
        CellTemperatureKitchen,
        CellTemperatureBedroom,
    ]


class GridColumnElectricity(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[3]
    cells = [
        CellElectricityDemand,
        CellElectricityRate,
        CellElectricityAccumulativeCost,
        CellBatteryLevel,
        CellBatteryChargeRemainingTime,
        CellBatteryDischargeRemainingTime,
    ]


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    columns = [
        GridColumnSwitches,
        GridColumnSensors,
        GridColumnHomeLab,
        GridColumnTemperature,
        GridColumnElectricity,
    ]
