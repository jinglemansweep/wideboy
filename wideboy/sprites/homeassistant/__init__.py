import html
import logging
import pygame
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import Optional
from wideboy.constants import EVENT_EPOCH_MINUTE

# from wideboy.mqtt.homeassistant import HASS
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import load_image, render_text, render_material_icon
from wideboy.config import settings

logger = logging.getLogger("sprite.hassentitytile")


class HomeAssistantTemplateSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        template: str,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 12,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        color_outline: Optional[Color] = None,
        update_interval_mins: int = 5,
    ) -> None:
        super().__init__(scene, rect)
        self.template = template
        self.font_name = font_name
        self.font_size = font_size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.update_interval_min = update_interval_mins
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
                event.type == EVENT_EPOCH_MINUTE
                and event.unit % self.update_interval_min == 0
            ):
                self.render()

    def render(self) -> None:
        template_str = self.scene.engine.hass.client.get_rendered_template(
            self.template
        )
        template_text = render_text(
            template_str,
            self.font_name,
            self.font_size,
            color_fg=self.color_fg,
            color_bg=self.color_bg,
            color_outline=self.color_outline,
        )
        self.image = Surface(
            (template_text.get_rect().width, template_text.get_rect().height), SRCALPHA
        )
        self.image.fill(self.color_bg)
        self.image.blit(template_text, (0, 0))
        self.dirty = 1
