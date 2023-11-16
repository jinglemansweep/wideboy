import enum
import random
import time
from datetime import datetime
from typing import Callable, List, Dict, Tuple, cast

# NOTES

# TODO
#
# - Use pygame.sprite.Groups in TileGridColumn to position TileGridCells
# - Use pygame.sprite.Group in TileGrid to position TileGridColumns
# - Add these to another group for blitting
# - Only TileGrid should have a surface that gets blitted from the composite group

# +------------------------------------------------------+
# | TileGrid                                             |
# | +-------------------+ +-------------------+          |
# | | TileGridColumn    | | TileGridColumn    |          |
# | | +---------------+ | | +---------------+ |          |
# | | | TileGridCell  | | | | TileGridCell  | |          |
# | | +---------------+ | | +---------------+ |          |
# | | +---------------+ | | +---------------+ |          |
# | | | TileGridCell  | | | | TileGridCell  | |          |
# | | +---------------+ | | +---------------+ |          |
# | +-------------------+ +-------------------+          |
# +------------------------------------------------------+


class AnimatorState(enum.Enum):
    OPEN = 1
    CLOSED = 2
    OPENING = 3
    CLOSING = 4


class Animator:
    def __init__(self, range: Tuple[float, float], open=True, speed=1.0):
        self.range = range
        self.speed = speed
        self.open = open
        self.value = range[1] if open else range[0]

    @property
    def state(self):
        if self.open:
            return (
                AnimatorState.OPEN
                if self.value == self.range[1]
                else AnimatorState.OPENING
            )
        else:
            return (
                AnimatorState.CLOSED
                if self.value == self.range[0]
                else AnimatorState.CLOSING
            )

    def toggle(self):
        self.open = not self.open

    def set(self, open: bool):
        self.open = open

    def update(self):
        value = self.value + self.speed if self.open else self.value - self.speed
        if value > self.range[1]:
            value = self.range[1]
        elif value < self.range[0]:
            value = self.range[0]
        self.value = value

    def __repr__(self):
        return f"Animator(value={self.value}, open={self.open}, state={self.state}, range={self.range}, speed={self.speed})"


# TILE GRID


class BaseSprite:
    pass


class BaseGroup:
    pass


# should be a pygame.sprite.Sprite
class TileGridCell(BaseSprite):
    width: int
    height: int
    visible: bool = True
    label: str = ""

    def __repr__(self):
        return f"TileGridCell(size=({self.width}x{self.height}), visible={self.visible}, label='{self.label}')"


# should be a pygame.sprite.Group
class TileGridColumn(BaseGroup):
    cells: List[TileGridCell] = []

    def update(self, state):
        for cell in self.cells:
            cell.update(state)

    def __repr__(self):
        return f"TileGridColumn(open={self.open}, cells={len(self.cells)})"


# should be a pygame.sprite.Group
class TileGrid(BaseGroup):
    columns: List[TileGridColumn] = []
    state: Dict = dict()

    def __init__(self, state):
        self.state = state

    def __repr__(self):
        return f"TileGrid(columns={self.columns})"

    def update(self):
        for column in self.columns:
            column.update(self.state)


# CUSTOM SUBCLASSES


class VerticalCollapseTileGridCell(TileGridCell):
    width: int = 100
    height: int = 12
    height_animator: Animator

    @property
    def open(self):
        return self.height_animator.state != AnimatorState.CLOSED

    def __repr__(self):
        return f"VerticalCollapseTileGridCell(size=({self.width}x{self.height}), label='{self.label}', open={self.open}, height={self.height_animator.value})"


class HorizontalCollapseTileGridColumn(TileGridColumn):
    height: int = 12
    width_animator: Animator = Animator(range=(2.0, 64.0), open=True, speed=1.0)

    def update(self, state):
        super().update(state)
        self.width_animator.set(self.open)
        self.width_animator.update()

    @property
    def open(self):
        return any([cell.open for cell in self.cells])

    def __repr__(self):
        return f"HorizontalCollapseTileGridColumn(open={self.open}, width={self.width_animator.value}, cells={len(self.cells)})"


# CUSTOM TILES


class CellSpeedTestDownload(VerticalCollapseTileGridCell):
    label = "Download"

    def __init__(self):
        super().__init__()
        self.height_animator = Animator(range=(2.0, 12.0), open=True, speed=1.0)

    def update(self, state):
        v = int(state.get("download", 0))
        open = v < 500
        self.height_animator.set(open)
        self.height_animator.update()


class CellSpeedTestUpload(VerticalCollapseTileGridCell):
    label = "Upload"

    def __init__(self):
        super().__init__()
        self.height_animator = Animator(range=(2.0, 12.0), open=True, speed=1.0)

    def update(self, state):
        v = int(state.get("upload", 0))
        open = v < 500
        self.height_animator.set(open)
        self.height_animator.update()


# CUSTOM COLUMNS


class GridColumn1(HorizontalCollapseTileGridColumn):
    cells = [CellSpeedTestDownload(), CellSpeedTestUpload()]


# CUSTOM GRID


class MyTileGrid(TileGrid):
    x = 0
    y = 0
    columns = [GridColumn1()]


state: Dict = dict()
frame = 0

my_tile_grid = MyTileGrid(state)

while True:
    now = datetime.now()

    if frame % 100 == 0:
        state.update(
            dict(download=random.randint(0, 1000), upload=random.randint(0, 1000))
        )
        print(f"State: {state}")
        time.sleep(1)

    my_tile_grid.update()

    col0 = my_tile_grid.columns[0]
    cell0 = col0.cells[0]
    cell1 = col0.cells[1]

    print(f"COL0: {col0}, CELLS: {cell0}, {cell1}")

    time.sleep(0.05)
    frame += 1
