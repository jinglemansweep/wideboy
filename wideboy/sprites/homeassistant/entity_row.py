import logging
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

logger = logging.getLogger("sprite.hass_entity_row")


class HomeAssistantEntityTileOrientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class HomeAssistantEntityTile:
    visible: bool = True
    icon: int = MaterialIcons.MDI_DELETE
    icon_color: Color = Color(255, 255, 255, 255)
    label: str = ""
    label_color: Color = Color(255, 255, 255, 255)
    label_font_size: Optional[int] = None

    def process(self, state) -> None:
        pass


class HomeAssistantEntityRowSprite(BaseSprite):
    rect: Rect
    image: Surface
    orientation: HomeAssistantEntityTileOrientation

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        entities: List[HomeAssistantEntityTile],
        min_size: Tuple[Optional[int], Optional[int]] = (None, None),
        orientation: HomeAssistantEntityTileOrientation = HomeAssistantEntityTileOrientation.HORIZONTAL,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 10,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 255),
        color_outline: Optional[Color] = None,
        padding_right: int = 3,
        padding_bottom: int = 0,
        show_all: bool = False,
    ) -> None:
        super().__init__(scene, rect)
        self.entities = entities
        self.min_size = min_size
        self.orientation = orientation
        self.font_name = font_name
        self.font_size = font_size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.padding_right = padding_right
        self.padding_bottom = padding_bottom
        self.show_all = show_all
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
        if self.orientation == HomeAssistantEntityTileOrientation.HORIZONTAL:
            self.render_horizontal()
        elif self.orientation == HomeAssistantEntityTileOrientation.VERTICAL:
            self.render_vertical()

    def render_horizontal(self) -> None:
        w, h = 1, 2
        surfaces = []
        for entity in self.entities:
            entity.process(self.scene.hass.state)
            try:
                if not entity.visible:
                    continue
                entity_surface = render_hass_tile(
                    icon_codepoint=entity.icon,
                    icon_color=entity.icon_color,
                    label_text=entity.label,
                    label_color=entity.label_color,
                    label_font_size=entity.label_font_size or self.font_size,
                    padding_right=self.padding_right,
                )
                w += entity_surface.get_rect().width
                h = max(h, entity_surface.get_rect().height)
                surfaces.append(entity_surface)
            except Exception as ex:
                logger.warn(f"failed to render entity", exc_info=ex)
        self.image = Surface((w, h - 1), SRCALPHA)
        self.image.fill(self.color_bg)
        x = 0
        for surface in surfaces:
            self.image.blit(surface, (x, 0))
            x += surface.get_rect().width
        if self.min_size[0] is not None:
            self.rect.width = self.min_size[0]
        else:
            self.rect.width = x
        self.dirty = 1

    def render_vertical(self) -> None:
        w, h = 1, 1
        surfaces = []
        for entity in self.entities:
            entity.process(self.scene.hass.state)
            try:
                if not entity.visible:
                    continue
                entity_surface = render_hass_tile(
                    icon_codepoint=entity.icon,
                    icon_color=entity.icon_color,
                    label_text=entity.label,
                    label_color=entity.label_color,
                    label_font_size=entity.label_font_size or self.font_size,
                    padding_right=self.padding_right,
                )
                h += entity_surface.get_rect().height - 3 + self.padding_bottom
                w = max(w, entity_surface.get_rect().width)
                surfaces.append(entity_surface)
            except Exception as ex:
                logger.warn(f"failed to render entity", exc_info=ex)
        if self.min_size[0] is not None:
            w = self.min_size[0]
        if self.min_size[1] is not None:
            h = self.min_size[1]
        self.image = Surface((w, h), SRCALPHA)
        self.image.fill(self.color_bg)
        y = 0
        for surface in surfaces:
            self.image.blit(surface, (0, y))
            y += surface.get_rect().height - 3 + self.padding_bottom
        self.rect.height = y
        self.dirty = 1


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
