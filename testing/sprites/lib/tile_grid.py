import enum
import logging
import pygame
import random
import time
from datetime import datetime
from typing import Any, Callable, List, Dict, Tuple, Type, TypeVar, cast

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

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# ANIMATION HELPERS


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

TILE_GRID_CELL_WIDTH = 64
TILE_GRID_CELL_HEIGHT = 12


class BaseGroup(pygame.sprite.Group):
    pass


class BaseSprite(pygame.sprite.Sprite):
    pass


class TileGridCell(BaseSprite):
    color_background: pygame.Color = pygame.Color(0, 0, 0, 0)
    width: int = TILE_GRID_CELL_WIDTH
    height: int = TILE_GRID_CELL_HEIGHT
    visible: bool = True
    label: str = ""

    def __init__(self, state):
        super().__init__(state)
        self.state = state
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color_background)
        self.rect = self.image.get_rect()

    def update(self):
        self.render(self.state)

    def render(self, state):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.color_background)
        self.rect = self.image.get_rect()

    def __repr__(self):
        return f"TileGridCell(size=({self.width}x{self.height}), visible={self.visible}, label='{self.label}')"


class TileGridColumn(BaseSprite):
    width: int = TILE_GRID_CELL_WIDTH
    height: int = 0
    cells: List[Any]

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.cells_inst = [cell(self.state) for cell in self.cells]
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def update(self):
        self.render()

    def render(self):
        ch = 0
        mh = sum([cell.image.get_height() for cell in self.cells_inst])
        self.image = pygame.Surface((self.rect.width, mh))
        self.image.fill((0, 0, 0))
        for cell in self.cells_inst:
            cell.update()
            self.image.blit(cell.image, (0, ch))
            ch += cell.image.get_height()

    def __repr__(self):
        return f"TileGridColumn(open={self.open}, cells={len(self.cells)})"


class TileGrid(BaseSprite):
    columns: List[Any]
    state: Dict = dict()

    def __init__(self, state, x=0, y=0):
        super().__init__()
        self.state = state
        self.columns_inst = [column(self.state) for column in self.columns]
        self.image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return f"TileGrid(columns={self.groups})"

    def update(self):
        self.render()

    def render(self):
        cw = 0
        mw = sum([column.image.get_width() for column in self.columns_inst])
        mh = max([column.image.get_width() for column in self.columns_inst])
        self.image = pygame.Surface((mw, mh))
        self.rect.width = mw
        self.rect.height = mh
        self.image.fill((0, 0, 0, 0))
        for column in self.columns_inst:
            column.update()
            self.image.blit(column.image, (cw, 0))
            cw += column.image.get_width()


# CUSTOM SUBCLASSES


class VerticalCollapseTileGridCell(TileGridCell):
    width: int = TILE_GRID_CELL_WIDTH
    height_animator: Animator

    def __init__(self, state):
        super().__init__(state)
        self.height_animator = Animator(range=(0.0, 12.0), open=True, speed=1.0)

    def update(self):
        self.height_animator.update()
        self.rect.height = self.height_animator.value
        super().update()

    @property
    def open(self):
        return self.height_animator.state != AnimatorState.CLOSED

    def __repr__(self):
        return f"VerticalCollapseTileGridCell(size=({self.width}x{self.height}), label='{self.label}', open={self.open}, height={self.height_animator.value})"


class HorizontalCollapseTileGridColumn(TileGridColumn):
    height: int = TILE_GRID_CELL_HEIGHT
    width_animator: Animator

    def __init__(self, state):
        super().__init__(state)
        self.width_animator = Animator(range=(2.0, 64.0), open=True, speed=1.0)

    def update(self):
        self.width_animator.set(self.open)
        self.width_animator.update()
        self.rect.width = self.width_animator.value
        super().update()

    @property
    def open(self):
        return any([cell.open for cell in self.cells_inst])

    def __repr__(self):
        return f"HorizontalCollapseTileGridColumn(open={self.open}, width={self.width_animator.value}, cells={len(self.cells)})"
