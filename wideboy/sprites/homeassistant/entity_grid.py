import logging
import pygame
import random
import types
from enum import Enum
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import Optional, List, Set, Dict, Any, Union, Tuple
from wideboy.constants import (
    EVENT_EPOCH_MINUTE,
    EVENT_HASS_STATESTREAM_UPDATE,
)

from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    MaterialIcons,
    render_text,
    render_material_icon,
)

logger = logging.getLogger("sprite.hass_entity_grid")


class HomeAssistantEntityGridTile:
    visible: bool = True
    icon: Optional[Union[int, str]] = None
    icon_color_bg: Color = Color(0, 0, 0, 255)
    icon_color_fg: Color = Color(255, 255, 255, 255)
    label: str = ""
    label_align: str = "left"
    label_color_bg: Color = Color(0, 0, 0, 0)
    label_color_fg: Color = Color(255, 255, 255, 255)
    label_color_outline: Color = Color(0, 0, 0, 255)
    label_font: str = "fonts/bitstream-vera.ttf"
    label_font_size: int = 12
    progress: float = 1.0

    def process(self, state) -> None:
        pass


class HomeAssistantEntityGridSprite(BaseSprite):
    rect: Rect
    image: Surface
    row_height: int = 14
    accent_bar_width: int = 4

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        cells: List[HomeAssistantEntityGridTile] = [],
        alpha: int = 192,
        accent_color: Color = Color(255, 0, 0, 255),
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 12,
    ) -> None:
        super().__init__(scene, rect)
        self.cells = cells
        self.alpha = alpha
        self.accent_color = accent_color
        self.font_name = font_name
        self.font_size = font_size
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if (
                event.type == EVENT_HASS_STATESTREAM_UPDATE
                or event.type == EVENT_EPOCH_MINUTE
            ):
                self.render()

    def render(self) -> None:
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.image.fill(Color(0, 0, 0, self.alpha))
        self.image.fill(
            self.accent_color, (0, 0, self.accent_bar_width, self.rect.height)
        )
        cx, cy = self.accent_bar_width, 0
        for cell_idx, cell in enumerate(self.cells):
            cell.process(self.scene.hass.state)
            if not cell.visible:
                continue
            self.image.blit(
                render_hass_tile_cell(
                    (self.rect.width - self.accent_bar_width, self.row_height), cell
                ),
                (cx, cy),
            )
            cy += self.row_height + 1
        self.dirty = 1


def render_hass_tile_cell(size: Tuple[int, int], cell: HomeAssistantEntityGridTile):
    surface = Surface(size, SRCALPHA)
    icon_width = 12
    if cell.icon is not None:
        icon_bg_surface = Surface((size[1], size[1]), SRCALPHA)
        icon_bg_surface.fill(cell.icon_color_bg)
        surface.blit(icon_bg_surface, (0, 0))
        ix, iy = 0, 0
        if isinstance(cell.icon, str):
            icon_surface = render_text(
                cell.icon.upper(),
                cell.label_font,
                cell.label_font_size,
                color_fg=cell.icon_color_fg,
                color_bg=cell.icon_color_bg,
            )
            ix += (icon_surface.get_rect().width // 2) - 2
            iy -= 1
        else:
            icon_surface = render_material_icon(
                cell.icon,
                size[1],
                cell.icon_color_fg,
            )
        surface.blit(icon_surface, (ix + 1, iy))
    cx, cy = 0, 0
    cx += icon_width + 1
    label_background_surface = Surface(
        ((size[0] - icon_width) * cell.progress, size[1]), SRCALPHA
    )
    label_background_surface.fill(cell.label_color_bg)
    surface.blit(label_background_surface, (cx + 3, cy))
    label_surface = render_text(
        cell.label,
        font_filename=cell.label_font,
        font_size=cell.label_font_size,
        color_fg=cell.label_color_fg,
        color_outline=cell.label_color_outline,
    )
    if cell.label_align == "right":
        label_x = size[0] - label_surface.get_rect().width
    elif cell.label_align == "center":
        label_x = cx + (label_surface.get_rect().width // 2)
    else:
        label_x = cx + 4
    surface.blit(label_surface, (label_x, -2))
    return surface
