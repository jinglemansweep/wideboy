import pygame
from .lib.tile_grid import (
    TileGrid,
    HorizontalCollapseTileGridColumn,
    VerticalCollapseTileGridCell,
)

# CUSTOM TILES


class CellSpeedTestDownload(VerticalCollapseTileGridCell):
    label = "Download"
    color_background = pygame.Color(32, 0, 0, 255)

    def update(self, state):
        super().update(state)
        v = int(state.get("download", 0))
        open = v > 500
        self.height_animator.set(open)


class CellSpeedTestUpload(VerticalCollapseTileGridCell):
    label = "Upload"
    color_background = pygame.Color(0, 32, 0, 255)

    def update(self, state):
        super().update(state)
        v = int(state.get("upload", 0))
        open = v > 500
        self.height_animator.set(open)


# CUSTOM COLUMNS


class GridColumn1(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestUpload(), CellSpeedTestDownload()]


class GridColumn2(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestDownload()]


# CUSTOM GRID


class CustomTileGrid(TileGrid):
    x = 0
    y = 0
    columns = [GridColumn1(), GridColumn2()]
