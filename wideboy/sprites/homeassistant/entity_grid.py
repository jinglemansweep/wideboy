import logging
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
    label_font_size: int = 10
    progress: float = 1.0

    def process(self, state) -> None:
        pass


"""
class TestDemandTile(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOWNLOAD
    bg_brightness = 0.5

    def process(self, state):
        value = state.get("sensor.octopus_energy_electricity_current_demand", 0)
        self.label = f"{value:.0f}w"
        percent_float = float(min(value, 1000) / 1000)
        percent_float = random.random()
        self.icon_color_bg = Color(0, 0, 0, 255)
        self.icon_color_fg = Color(255, 255, 255, 255)
        if 0 < percent_float < 0.3:
            self.label_color_bg = Color(0, 255 * self.bg_brightness, 0, 255)
        elif 0.3 <= percent_float < 0.6:
            self.label_color_bg = Color(
                255 * self.bg_brightness, 255 * self.bg_brightness, 0, 255
            )
        elif 0.6 <= percent_float <= 1.0:
            self.label_color_bg = Color(255 * self.bg_brightness, 0, 0, 255)
            self.icon_color_bg = Color(255, 0, 0, 255)
            self.icon_color_fg = Color(255, 255, 255, 255)
        self.progress = percent_float


class TestTile(HomeAssistantEntityGridTile):
    icon = MaterialIcons.MDI_DOWNLOAD

    def process(self, state):
        value = state.get("sensor.speedtest_download_average", 0)
        self.label = f"{value:.0f}M"
        # self.label_align = random.choice(["left", "right"])
        self.icon = random.choice(
            [MaterialIcons.MDI_DOWNLOAD, MaterialIcons.MDI_UPLOAD, None, "A", "b", "1"]
        )
        self.progress = random.random()
        self.label_color_bg = Color(255, 255, 0, 255)

        invert = random.choice([True, False])
        self.icon_color_fg = (
            Color(255, 255, 255, 255) if invert else Color(0, 0, 0, 255)
        )
        self.icon_color_bg = (
            Color(0, 0, 0, 255) if invert else Color(255, 255, 255, 255)
        )
"""


class HomeAssistantEntityGridSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        cell_size: Tuple[int, int] = (64, 12),
        title: Optional[str] = None,
        cells: List[HomeAssistantEntityGridTile] = [],
        alpha: int = 192,
        accent_color: Color = Color(255, 0, 0, 255),
        padding: Tuple[int, int] = (0, 0),
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 10,
    ) -> None:
        super().__init__(scene, rect)
        self.cell_size = cell_size
        self.title = title
        self.cells = cells
        self.alpha = alpha
        self.accent_color = accent_color
        self.padding = padding
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
        bx, by = self.padding[0], self.padding[1]
        cx, cy = bx, by
        if self.title is not None:
            title_surface = render_text(
                self.title,
                self.font_name,
                self.font_size,
                color_fg=Color(255, 255, 255, 255),
                color_outline=Color(0, 0, 0, 255),
            )
            self.image.blit(title_surface, (cx + 1, cy - 2))
            by += title_surface.get_rect().height - 3
        self.image.fill(self.accent_color, (bx, by, self.rect.width, 1))
        by += 2
        cy = by
        for cell_idx, cell in enumerate(self.cells):
            cell.process(self.scene.hass.state)
            if not cell.visible:
                continue
            self.image.blit(
                render_hass_tile_cell(self.cell_size, cell),
                (cx, cy),
            )
            cy += self.cell_size[1] + 1
        cy = by
        cx += self.cell_size[0]
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
        surface.blit(icon_surface, (ix, iy))
    cx, cy = 0, 0
    cx += icon_width
    label_background_surface = Surface(
        ((size[0] - icon_width) * cell.progress, size[1]), SRCALPHA
    )
    label_background_surface.fill(cell.label_color_bg)
    surface.blit(label_background_surface, (cx, cy))
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
        label_x = cx
    surface.blit(label_surface, (label_x, -2))
    return surface


def render_hass_tile(
    icon_codepoint: Optional[int] = None,
    icon_color: Color = Color(255, 255, 255, 255),
    icon_size: int = 11,
    label_text: Optional[str] = None,
    label_font_name: str = "fonts/bitstream-vera.ttf",
    label_font_size: int = 10,
    label_color: Color = Color(255, 255, 255, 255),
    bg_color: Color = Color(0, 0, 0, 0),
    outline_color: Color = Color(0, 0, 0, 255),
    padding_right: int = 0,
) -> Surface:
    w, h = 0, 0
    icon_surface = None
    # logger.debug(f"render_hass_tile: state={state.dict()}")
    if icon_codepoint:
        icon_surface = render_material_icon(
            icon_codepoint, icon_size, icon_color, outline_color
        )
        w += icon_surface.get_rect().width
        h = icon_surface.get_rect().height
    label_surface = None
    if label_text:
        label_surface = render_text(
            label_text,
            label_font_name,
            label_font_size,
            color_fg=label_color,
            color_bg=bg_color,
            color_outline=outline_color,
        )
        w += label_surface.get_rect().width
        h = max(h, label_surface.get_rect().height)
    surface = Surface((w + padding_right, h), SRCALPHA)
    x = 0
    if icon_surface is not None:
        surface.blit(icon_surface, (x, 0))
        x += icon_surface.get_rect().width
    if label_surface is not None:
        surface.blit(label_surface, (x, -1))
        x += label_surface.get_rect().width
    return surface
