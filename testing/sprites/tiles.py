import datetime
import enum
import pygame
import random
from .lib.tile_grid import (
    TileGrid,
    FontAwesomeIcons,
    HorizontalCollapseTileGridColumn,
    VerticalCollapseTileGridCell,
)

# CUSTOM COLORS


class CustomColor(enum.Enum):
    RED_DARK = pygame.Color(64, 0, 0, 255)
    RED = pygame.Color(255, 0, 0, 255)
    BLUE_DARK = pygame.Color(0, 0, 64, 255)
    BLUE = pygame.Color(0, 0, 255, 255)
    GREEN_DARK = pygame.Color(0, 64, 0, 255)
    GREEN = pygame.Color(0, 255, 0, 255)
    YELLOW_DARK = pygame.Color(64, 64, 0, 255)
    YELLOW = pygame.Color(255, 255, 0, 255)
    ORANGE_DARK = pygame.Color(64, 32, 0, 255)
    ORANGE = pygame.Color(255, 128, 0, 255)
    PURPLE_DARK = pygame.Color(64, 0, 64, 255)
    PURPLE = pygame.Color(255, 0, 255, 255)
    PINK_DARK = pygame.Color(64, 0, 32, 255)
    PINK = pygame.Color(255, 0, 128, 255)
    CYAN_DARK = pygame.Color(0, 64, 64, 255)
    CYAN = pygame.Color(0, 255, 255, 255)
    WHITE = pygame.Color(255, 255, 255, 255)
    BLACK = pygame.Color(0, 0, 0, 255)
    TRANSPARENT = pygame.Color(0, 0, 0, 0)


# CUSTOM SUBCLASSES


class GridCell(VerticalCollapseTileGridCell):
    pass


# Electricity Tiles


class CellElectricityDemand(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BOLT

    def update(self):
        super().update()
        v = int(self.state.get("sensor.octopus_energy_electricity_current_demand", 0))
        self.label = f"{v}"
        open = v > 500
        self.height_animator.set(open)
        self.icon_color_background = (
            CustomColor.RED_DARK.value if v > 1000 else CustomColor.TRANSPARENT.value
        )


class CellElectricityRate(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HOURGLASS

    def update(self):
        super().update()
        v = float(self.state.get("sensor.octopus_energy_electricity_current_rate", 0))
        self.label = f"{v}"


class CellElectricityAccumulativeCost(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CLOCK

    def update(self):
        super().update()
        v = float(
            self.state.get(
                "sensor.octopus_energy_electricity_current_accumulative_cost", 0
            )
        )
        self.label = f"{v}"


# Battery Tiles


class CellBatteryLevel(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_BATTERY_FULL

    def update(self):
        super().update()
        v = int(self.state.get("sensor.delta_2_max_downstairs_battery_level", 0))
        self.label = f"{v}"


class CellBatteryACInput(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_PLUS

    def update(self):
        super().update()
        v = int(self.state.get("sensor.delta_2_max_downstairs_ac_in_power", 0))
        self.label = f"{v}"

        open = v > 100
        self.height_animator.set(open)


class CellBatteryACOutput(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_PLUG_CIRCLE_MINUS

    def update(self):
        super().update()
        v = int(self.state.get("sensor.delta_2_max_downstairs_ac_out_power", 0))
        self.label = f"{v}"
        open = v > 100
        self.height_animator.set(open)


# Network Tiles


class CellSpeedTestDownload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_DOWN

    def update(self):
        super().update()
        v = int(self.state.get("sensor.speedtest_download_average", 0))
        self.label = f"{v}Mb"
        open = v > 500
        self.height_animator.set(open)


class CellSpeedTestUpload(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_CIRCLE_ARROW_UP

    def update(self):
        super().update()
        v = int(self.state.get("sensor.speedtest_upload_average", 0))
        self.label = f"{v}Mb"

        open = v > 500
        self.height_animator.set(open)


class CellSpeedTestPing(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HEART_PULSE

    def update(self):
        super().update()
        v = int(self.state.get("sensor.speedtest_ping_average", 0))
        self.label = f"{v}ms"
        open = v > 25
        self.height_animator.set(open)


class CellDS920VolumeUsage(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_HARD_DRIVE

    def update(self):
        super().update()
        v = int(self.state.get("sensor.ds920plus_volume_used", 0))
        self.label = f"{v}"

        open = v > 25
        self.height_animator.set(open)


# Test Tiles


class CellTestRandom(GridCell):
    icon_codepoint = FontAwesomeIcons.ICON_FA_DICE_THREE

    def update(self):
        super().update()
        v = datetime.datetime.now().second
        self.label = f"{v}"

        open = 0 <= v % 5 <= 2
        self.height_animator.set(open)


# Switch Tiles


class CellSwitchLoungeFan(GridCell):
    label = "Fan"
    icon_codepoint = FontAwesomeIcons.ICON_FA_FAN

    def update(self):
        super().update()
        v = int(self.state.get("fan", 0))

        open = v > 90
        self.height_animator.set(open)


# CUSTOM COLUMNS


class GridColumnNetwork(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = CustomColor.RED.value
    cells = [
        CellSpeedTestDownload,
        CellSpeedTestUpload,
        # CellSpeedTestPing,
        # CellDS920VolumeUsage,
    ]


class GridColumnTest(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = CustomColor.GREEN.value
    cells = [CellTestRandom]


class GridColumnBattery(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = CustomColor.BLUE.value
    cells = [
        CellBatteryLevel,
        CellBatteryACInput,
        CellBatteryACOutput,
    ]


class GridColumnElectricity(HorizontalCollapseTileGridColumn):
    border_width = 1
    border_color = CustomColor.YELLOW.value
    cells = [
        CellElectricityDemand,
        CellElectricityRate,
        CellElectricityAccumulativeCost,
    ]


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    columns = [
        GridColumnNetwork,
        GridColumnTest,
        GridColumnBattery,
        GridColumnElectricity,
    ]
