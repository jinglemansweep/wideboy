import pygame
from .lib.tile_grid import (
    TileGrid,
    HorizontalCollapseTileGridColumn,
    VerticalCollapseTileGridCell,
    CellStyle,
)

# CUSTOM STYLES


class StyleRedBackground(CellStyle):
    color_background = pygame.Color(128, 0, 0, 255)


class StyleGreenBackground(CellStyle):
    color_background = pygame.Color(0, 128, 0, 255)


class StyleBlueBackground(CellStyle):
    color_background = pygame.Color(0, 0, 128, 255)


# CUSTOM TILES


class CellSpeedTestDownload(VerticalCollapseTileGridCell):
    style = StyleRedBackground()

    def update(self):
        super().update()
        v = int(self.state.get("download", 0))
        self.label = f"{v}Mb"
        open = v > 500
        self.height_animator.set(open)


class CellSpeedTestUpload(VerticalCollapseTileGridCell):
    style = StyleGreenBackground()

    def update(self):
        super().update()
        v = int(self.state.get("upload", 0))
        self.label = f"{v}Mb"
        open = v > 500
        self.height_animator.set(open)


class CellSpeedTestPing(VerticalCollapseTileGridCell):
    style = StyleBlueBackground()

    def update(self):
        super().update()
        v = int(self.state.get("ping", 0))
        self.label = f"{v}ms"
        open = v > 25
        self.height_animator.set(open)


class CellSwitchLoungeFan(VerticalCollapseTileGridCell):
    label = "Fan"

    def update(self):
        super().update()
        v = int(self.state.get("fan", 0))
        open = v > 90
        self.height_animator.set(open)


# CUSTOM COLUMNS


class GridColumn1(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestUpload, CellSpeedTestDownload, CellSpeedTestPing]


class GridColumn2(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestDownload]


class GridColumn3(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestPing, CellSwitchLoungeFan]


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    columns = [GridColumn1, GridColumn2, GridColumn3]
