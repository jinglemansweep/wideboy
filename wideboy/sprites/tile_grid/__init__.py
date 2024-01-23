import logging
from pygame import Color, Surface, SRCALPHA
from pygame.sprite import LayeredDirty, DirtySprite
from typing import Any, Dict, List, Tuple, Type
from ..animation import Animator, AnimatorState
from .helpers import (
    FontAwesomeIcons,
    render_icon,
    render_text,
    is_defined,
)

# NOTES

logger = logging.getLogger("sprites.tile_grid")

# CONSTANTSf

TILE_GRID_CELL_WIDTH = 64
TILE_GRID_CELL_HEIGHT = 12
TILE_GRID_CELL_ICON_WIDTH = 15
TILE_GRID_CELL_ICON_HEIGHT = 12

# TILE GRID

# Mixins


class StyleMixin:
    # Cell
    cell_color_background: Color = Color(16, 16, 16, 64)
    # Label
    label_antialias: bool = True
    label_outline: bool = True
    label_color_foreground: Color = Color(255, 255, 255, 255)
    label_color_outline: Color = Color(0, 0, 0, 255)
    # Icon
    icon_visible: bool = True
    icon_codepoint: int = FontAwesomeIcons.ICON_FA_BOLT
    icon_width: int = TILE_GRID_CELL_ICON_WIDTH
    icon_height: int = TILE_GRID_CELL_ICON_HEIGHT
    icon_color_background: Color = Color(32, 32, 32, 255)
    icon_color_foreground: Color = Color(255, 255, 255, 255)


# Tile Grid Cell Sprites


class TileGridCell(DirtySprite, StyleMixin):
    image: Surface
    style: Dict
    entity_id: str = ""
    width: int = TILE_GRID_CELL_WIDTH
    height: int = TILE_GRID_CELL_HEIGHT
    label: str = ""

    def __init__(self, state) -> None:
        super().__init__()
        self.state = state
        self.image = Surface((self.width, self.height), SRCALPHA)
        self.image.fill(self.cell_color_background)
        self.rect = self.image.get_rect()

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        self.dirty = 1

    def render(self) -> Surface:
        image = Surface((self.width, self.height), SRCALPHA)
        image.fill(self.cell_color_background)
        cx, cy = 0, 0
        if self.icon_visible:
            icon_surface = render_icon(
                self.icon_width,
                self.icon_height,
                self.icon_codepoint,
                self.icon_color_background,
                self.icon_color_foreground,
            )
            image.blit(icon_surface, (0, 0))
            cx += icon_surface.get_width()
        label_surface = render_text(
            text=self.label,
            antialias=self.label_antialias,
            color_foreground=self.label_color_foreground,
            color_outline=self.label_color_outline,
            padding=(2, 1),
            outline=self.label_outline,
        )
        image.blit(label_surface, (cx, cy))
        return image

    def __repr__(self) -> str:
        return f"TileGridCell(size=({self.width}x{self.height}), visible={self.visible}, label='{self.label}')"

    @property
    def entity_state(self):
        return self.state.get(self.entity_id, dict())

    @property
    def value(self) -> Any:
        state = self.entity_state.get("state", None)
        if state is None:
            return None
        elif state.lower() in ["on", "true"]:
            return True
        elif state.lower() in ["off", "false"]:
            return False
        else:
            try:
                return float(state)
            except ValueError:
                return state


# Tile Grid Column Group


class TileGridColumn(LayeredDirty):
    animator: Animator

    def __init__(self, *sprites: TileGridCell) -> None:
        super().__init__()
        self.add(sprites)
        self.animator = Animator(range=(0.0, 64.0), open=False, speed=1.0)

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
        open = any(
            [
                sprite
                for sprite in self.sprites()
                if hasattr(sprite, "open") and sprite.open
            ]
        )
        self.animator.set(open)
        self.animator.update()
        if self.animating:
            self.dirty = 1

    @property
    def animating(self) -> bool:
        return self.animator.animating or any(
            [cell.animating for cell in self.sprites() if hasattr(cell, "animating")]
        )


# Tile Grid Sprite


class TileGrid(DirtySprite):
    state: Dict
    columns: List
    tile_surface_cache: Dict[str, Surface] = dict()

    def __init__(self, cells: List[List[Type[TileGridCell]]], state: Dict) -> None:
        super().__init__()
        self.image = Surface((0, 0), SRCALPHA)
        self.rect = self.image.get_rect()
        self.cells = cells
        self.state = state
        self.columns = []

        for column in self.cells:
            column_group: TileGridColumn = TileGridColumn()
            for cell in column:
                cell_instance = cell(self.state)
                column_group.add(cell_instance)
            self.columns.append(column_group)

    def __repr__(self) -> str:
        return f"TileGrid(columns={self.columns})"

    def update(self, entity_id=None):
        dirty = False
        cx, cy = 0, 0
        width, height = self.calculate_size()
        animating = any([column.animating for column in self.columns])
        if animating:
            dirty = True
        self.image = Surface((width, height), SRCALPHA)
        self.image.fill(Color(0, 0, 0, 0))
        for column in self.columns:
            cy = 0
            for cell in column.sprites():
                if (
                    cell.entity_id not in self.tile_surface_cache
                    or entity_id == cell.entity_id
                ):
                    cell.update()
                    cell_surface = cell.render()
                    self.tile_surface_cache[cell.entity_id] = cell_surface
                cell.image = self.tile_surface_cache[cell.entity_id]
                cell.rect.width = column.animator.value
                cell.rect.x = cx
                cell.rect.y = cy
                cy += cell.rect.height
            cx += column.animator.value
            column.update()
            column.draw(self.image)
        self.rect.width, self.rect.height = self.calculate_size()
        self.dirty = 1 if dirty else 0

    def calculate_size(self) -> Tuple[int, int]:
        width = 0
        height = 0
        for column in self.columns:
            width += column.animator.value
            height = max(height, sum([cell.rect.height for cell in column.sprites()]))
        return width, height


# USEFUL SUBCLASSES


class TallGridCell(TileGridCell):
    width: int = TILE_GRID_CELL_WIDTH
    height: int = TILE_GRID_CELL_HEIGHT * 2
    open: bool = True
    icon_visible: bool = False

    def __init__(self, state) -> None:
        super().__init__(state)
        self.image = Surface((self.width, self.height), SRCALPHA)
        self.image.fill(Color(255, 255, 255, 255))
        self.rect = self.image.get_rect()


class VerticalCollapseTileGridCell(TileGridCell):
    width: int = TILE_GRID_CELL_WIDTH
    height_animator: Animator

    def __init__(self, state) -> None:
        super().__init__(state)
        self.height_animator = Animator(range=(0.0, 12.0), open=self.open, speed=1.0)

    def update(self, *args, **kwargs):
        self.height_animator.set(self.open)
        self.height_animator.update()
        self.rect.height = self.height_animator.value
        crop_surface = Surface((self.width, self.rect.height), SRCALPHA)
        crop_surface.blit(self.image, (0, 0, self.width, self.rect.height))
        self.image = crop_surface
        super().update(*args, **kwargs)

    @property
    def open_finished(self) -> bool:
        return self.height_animator.state != AnimatorState.CLOSED

    @property
    def close_finished(self) -> bool:
        return self.height_animator.state != AnimatorState.OPEN

    @property
    def animating(self) -> bool:
        return self.height_animator.animating

    @property
    def open(self):
        return is_defined(self.value) and self.value

    def __repr__(self) -> str:
        return f"VerticalCollapseTileGridCell(size=({self.width}x{self.height}), label='{self.label}', open={self.open}, height={self.height_animator.value})"
