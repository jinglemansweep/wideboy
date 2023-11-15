import enum
import random
import time
from datetime import datetime
from typing import Callable, List, Dict, Tuple, cast

# COLLAPSIBLE MIXINS


def clamp(value, min_value, max_value):
    """Clamp value to the range [min_value, max_value]."""
    return max(min_value, min(value, max_value))


class AnimatorState(enum.Enum):
    OPEN = 1
    CLOSED = 2
    OPENING = 3
    CLOSING = 4


class Animator:
    def __init__(self, range: Tuple[float, float], start: float, open=True, speed=1.0):
        self.range = range
        self.start = start
        self.speed = speed
        self._open = open
        self._value = start

    @property
    def value(self):
        return self._value

    @property
    def open(self):
        return self._open

    @property
    def state(self):
        if self._open:
            return (
                AnimatorState.OPEN
                if self._value == self.range[1]
                else AnimatorState.OPENING
            )
        else:
            return (
                AnimatorState.CLOSED
                if self._value == self.range[0]
                else AnimatorState.CLOSING
            )

    def toggle(self):
        self._open = not self._open

    def set(self, open: bool):
        self._open = open

    def update(self):
        value = self._value + self.speed if self.open else self._value - self.speed
        self._value = clamp(value, self.range[0], self.range[1])

    def __repr__(self):
        return f"Animator(value={self.value}, open={self.open}, state={self.state}, range={self.range}, speed={self.speed})"


# TILE GRID


class BaseSprite:
    pass


class TileGridCell(BaseSprite):
    width: int
    height: int
    visible: bool = True
    label: str = ""

    def __repr__(self):
        return f"TileGridCell(size=({self.width}x{self.height}), visible={self.visible}, label='{self.label}')"


class TileGridColumn(BaseSprite):
    cells: List[TileGridCell] = []

    def update(self, state):
        for cell in self.cells:
            cell.update(state)

    def __repr__(self):
        return f"TileGridColumn(open={self.open}, cells={len(self.cells)}, visible={len(self.visible_cells)})"


class TileGrid(BaseSprite):
    columns: List[TileGridColumn] = []

    def __repr__(self):
        return f"TileGrid(columns={self.columns})"

    def update(self, state):
        for column in self.columns:
            column.update(state)


# CUSTOM SUBCLASSES


class VerticalCollapseTileGridCell(TileGridCell):
    width: int = 100
    height_animator: Animator = Animator(
        range=(0.0, 12.0), start=12.0, open=True, speed=1.0
    )

    def update(self, state):
        self.visible = state.get("visible", False)
        self.height_animator.set(self.visible)
        self.height_animator.update()

    @property
    def open(self):
        return self.height_animator.state != AnimatorState.CLOSED


class HorizontalCollapseTileGridColumn(TileGridColumn):
    height: int = 12
    width_animator: Animator = Animator(
        range=(2.0, 64.0), start=2.0, open=True, speed=1.0
    )

    def update(self, state):
        super().update(state)
        self.width_animator.set(self.open)
        self.width_animator.update()

    @property
    def visible_cells(self):
        return [cell for cell in self.cells if cell.visible]

    @property
    def open(self):
        return any([cell.open for cell in self.cells])

    def __repr__(self):
        return f"HorizontalCollapseTileGridColumn(open={self.open}, cells={len(self.cells)}, visible={len(self.visible_cells)})"


# CUSTOM TILES


class CellSpeedTestDownload(VerticalCollapseTileGridCell):
    label = "Download"


# CUSTOM COLUMNS


class GridColumn1(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestDownload()]


# CUSTOM GRID


class MyTileGrid(TileGrid):
    x = 0
    y = 0
    columns = [GridColumn1()]


state: Dict = dict()
frame = 0

my_tile_grid = MyTileGrid()

while True:
    now = datetime.now()

    if frame % 100 == 0:
        state.update({"visible": not state.get("visible", False)})
        print(f"State: {state}")

    my_tile_grid.update(state)

    col0 = my_tile_grid.columns[0]
    cell = col0.cells[0]

    if isinstance(col0, HorizontalCollapseTileGridColumn):
        print(
            f"COLUMN: value={col0.width_animator.value} state={col0.width_animator.state} open={col0.open}"
        )

    if isinstance(cell, VerticalCollapseTileGridCell):
        print(
            f"CELL: value={cell.height_animator.value} state={cell.height_animator.state} open={cell.open}"
        )

    time.sleep(0.05)
    frame += 1
