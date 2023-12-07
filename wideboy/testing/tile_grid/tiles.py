from wideboy.sprites.tile_grid import (
    TileGrid,
    VerticalCollapseTileGridCell,
    FontAwesomeIcons,
)
from wideboy.sprites.tile_grid.helpers import CommonColors

# CUSTOM SUBCLASSES


class GridCell(VerticalCollapseTileGridCell):
    cell_color_background = CommonColors.COLOR_GREY_DARK
    icon_color_background = CommonColors.COLOR_GREY


# CUSTOM FUNCTIONS


def format_watts(watts: int):
    return "{:.0f}W".format(watts) if watts < 1000 else "{:.1f}kW".format(watts / 1000)


# TILE DEFINITIONS


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


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    pass
