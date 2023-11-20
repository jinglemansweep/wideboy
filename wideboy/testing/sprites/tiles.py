import datetime
import enum
import pygame
import random
from .lib.tile_grid import (
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


# TILE DEFINITIONS

# Electricity Tiles


class CellElectricityDemand(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BOLT

    @property
    def value(self):
        return float(
            self.state.get("sensor.octopus_energy_electricity_current_demand", 0)
        )

    @property
    def open(self):
        return self.value > 500

    @property
    def label(self):
        return format_watts(self.value)

    @property
    def cell_color_background(self):
        return (
            CommonColors.COLOR_RED_DARK
            if self.value > 1000
            else CommonColors.COLOR_GREY_DARK
        )

    @property
    def icon_color_background(self):
        return CommonColors.COLOR_RED if self.value > 1000 else CommonColors.COLOR_GREY


class CellElectricityRate(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOURGLASS

    @property
    def value(self):
        return float(
            self.state.get("sensor.octopus_energy_electricity_current_rate", 0)
        )

    @property
    def label(self):
        return f"£{self.value:.2f}"


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


# Network Tiles


class CellSpeedTestDownload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_DOWN

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_download_average", 0))

    @property
    def open(self):
        return self.value > 500

    @property
    def label(self):
        return f"{self.value}Mb"


class CellSpeedTestUpload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_UP

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_upload_average", 0))

    @property
    def open(self):
        return self.value > 500

    @property
    def label(self):
        return f"{self.value}Mb"


class CellSpeedTestPing(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HEART_PULSE

    @property
    def value(self):
        return int(self.state.get("sensor.speedtest_ping_average", 0))

    @property
    def open(self):
        return self.value > 25

    @property
    def label(self):
        return f"{self.value}ms"


class CellDS920VolumeUsage(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HARD_DRIVE

    @property
    def value(self):
        return int(self.state.get("sensor.ds920plus_volume_used", 0))

    @property
    def open(self):
        return self.value > 60

    @property
    def label(self):
        return f"{self.value}%"


# Test Tiles


class CellTestRandom(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_DICE_THREE

    @property
    def value(self):
        return datetime.datetime.now().second

    @property
    def open(self):
        return 0 <= self.value % 5 <= 2

    @property
    def label(self):
        return f"{self.value}"


# Switch Tiles


class CellSwitchLoungeFan(GridCell):
    label = "Fan"
    icon_codepoint = FontAwesomeIcons.ICON_FA_FAN

    @property
    def value(self):
        return self.state.get("fan", "off")

    @property
    def open(self):
        return self.value == "on"


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


class GridColumnHomeLab(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[0]
    cells = [
        CellDS920VolumeUsage,
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        CellSpeedTestPing,
    ]


class GridColumnBattery(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[1]
    cells = [
        CellBatteryLevel,
        CellBatteryACInput,
        CellBatteryACOutput,
    ]


class GridColumnElectricity(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[2]
    cells = [
        CellElectricityDemand,
        CellElectricityRate,
        CellElectricityAccumulativeCost,
    ]


class GridColumnTest(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = rainbox_colors[3]
    cells = [CellTestRandom]


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    columns = [
        GridColumnHomeLab,
        # GridColumnTest,
        GridColumnBattery,
        GridColumnElectricity,
    ]
