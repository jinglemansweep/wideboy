import html
import logging
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import Optional
from wideboy.constants import EVENT_EPOCH_MINUTE
from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    load_image,
    render_text,
)
from wideboy.config import settings

logger = logging.getLogger("sprite.hassentitytile")


class HassEntityTileSprite(BaseSprite):
    MDI_DELETE = "E872"

    def __init__(
        self,
        rect: Rect,
        entity_id: str,
        icon: str,
        state_callback: Optional[callable] = None,
        color: Color = Color(255, 255, 255, 255),
        font_size: int = 24,
    ) -> None:
        super().__init__(rect)
        self.entity_id = entity_id
        self.icon = icon
        self.color = color
        self.font_size = font_size
        self.state_callback = state_callback
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
            if event.type == EVENT_EPOCH_MINUTE:
                self.render()

    def render(self) -> None:
        entity = HASS.get_entity(entity_id=self.entity_id)
        active = self.state_callback(entity) if self.state_callback else True
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        if active:
            icon_text = render_text(
                html.unescape(f"&#x{self.icon};"),
                "fonts/material-icons.ttf",
                self.font_size,
                self.color,
                color_outline=Color(0, 0, 0, 255),
            )
            self.image.blit(icon_text, (0, 0))
        self.dirty = 1
