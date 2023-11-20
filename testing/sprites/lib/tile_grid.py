import enum
import logging
import pygame
import random
import time
from datetime import datetime
from typing import Any, Callable, List, Dict, Optional, Tuple, Type, TypeVar, cast

from .helpers import Animator, AnimatorState, FontAwesomeIcons, render_icon, render_text
from .helpers import LABEL_FONT_FILENAME, LABEL_FONT_SIZE  # TO BE REMOVED

# NOTES

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


TILE_GRID_CELL_WIDTH = 64
TILE_GRID_CELL_HEIGHT = 12

TILE_GRID_CELL_ICON_WIDTH = 14
TILE_GRID_CELL_ICON_HEIGHT = 12

# STYLE CLASSES

TILE_GRID_STYLE_DEFAULT = {
    "cell_alpha": 255,
    "cell_color_background": pygame.Color(16, 16, 16, 255),
    "cell_color_border": pygame.Color(0, 0, 0, 0),
    "label_color_text": pygame.Color(255, 255, 255, 255),
    "label_color_outline": pygame.Color(0, 0, 0, 255),
    "label_font": LABEL_FONT_FILENAME,
    "label_size": LABEL_FONT_SIZE,
    "label_padding": (2, 1),
    "label_outline": True,
    "label_antialias": True,
    "icon_visible": True,
    "icon_width": TILE_GRID_CELL_ICON_WIDTH,
    "icon_height": TILE_GRID_CELL_ICON_HEIGHT,
    "icon_color_background": pygame.Color(32, 32, 32, 255),
    "icon_color_foreground": pygame.Color(255, 255, 255, 255),
    "icon_codepoint": None,
}


# TILE GRID

# Base Classes


class BaseGroup(pygame.sprite.Group):
    pass


class BaseSprite(pygame.sprite.Sprite):
    pass


# Tile Grid Cell Sprites


class TileGridCell(BaseSprite):
    style: Dict
    width: int = TILE_GRID_CELL_WIDTH
    height: int = TILE_GRID_CELL_HEIGHT
    visible: bool = True
    label: str = ""

    def __init__(self, state):
        super().__init__(state)
        self.state = state
        self.style = TILE_GRID_STYLE_DEFAULT.copy()
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.style["cell_color_background"])
        self.rect = self.image.get_rect()

    def update(self):
        self.render()

    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.style["cell_color_background"])
        cx, cy = 0, 0
        if self.style["icon_visible"]:
            icon_surface = render_icon(
                self.style["icon_width"],
                self.style["icon_height"],
                self.style["icon_codepoint"],
                self.style["icon_color_background"],
                self.style["icon_color_foreground"],
            )
            self.image.blit(icon_surface, (0, 0))
            cx += icon_surface.get_width()
        label_surface = render_text(
            text=self.label,
            font_filename=self.style["label_font"],
            font_size=self.style["label_size"],
            antialias=self.style["label_antialias"],
            color_foreground=self.style["label_color_text"],
            color_outline=self.style["label_color_outline"],
            padding=self.style["label_padding"],
            outline=self.style["label_outline"],
        )
        self.image.blit(label_surface, (cx, 0))
        self.rect = self.image.get_rect()

    def __repr__(self):
        return f"TileGridCell(size=({self.width}x{self.height}), visible={self.visible}, label='{self.label}')"


# Tile Grid Column Sprites


class TileGridColumn(BaseSprite):
    width: int = TILE_GRID_CELL_WIDTH
    height: int = 0
    border_width: int = 0
    border_color: pygame.Color = pygame.Color(96, 96, 96, 255)
    cells: List[Any]

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.cells_inst = [cell(self.state) for cell in self.cells]
        self.border_padding = self.border_width + 1 if self.border_width else 0
        self.image = pygame.Surface(
            (
                self.width + self.border_padding,
                self.height,
            )
        )
        self.rect = self.image.get_rect()

    def update(self):
        self.render()

    def render(self):
        ch = 0
        mh = sum([cell.image.get_height() for cell in self.cells_inst])
        self.image = pygame.Surface((self.rect.width, mh))
        self.image.fill(pygame.Color(0, 0, 0))
        for cell in self.cells_inst:
            cell.update()
            self.image.blit(cell.image, (self.border_padding, ch))
            ch += cell.image.get_height()
        self.image.fill(self.border_color, (0, 0, self.border_width, mh))

    def __repr__(self):
        return f"TileGridColumn(open={self.open}, cells={len(self.cells)})"


# Tile Grid Sprite


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
        self.rect.height = mh
        self.image.fill((0, 0, 0, 0))
        for column in self.columns_inst:
            column.update()
            self.image.blit(column.image, (cw, 0))
            cw += column.image.get_width()
        self.rect.width = cw


# USEFUL SUBCLASSES


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
        self.width_animator = Animator(range=(0.0, 64.0), open=True, speed=1.0)

    def update(self):
        self.width_animator.set(self.open)
        self.width_animator.update()
        self.rect.width = self.width_animator.value
        super().update()

    @property
    def open(self):
        return any([cell.open for cell in self.cells_inst])

    def __repr__(self):
        return f"HorizontalCollapseTileGridColumn(open={self.open}, width={self.width_animator.value}, cells={len(self.cells_inst)})"
