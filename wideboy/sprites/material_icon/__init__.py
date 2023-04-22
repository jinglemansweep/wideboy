import logging
from typing import Optional
from pygame import Color, Rect, Surface, SRCALPHA
from wideboy.sprites.image_helpers import render_material_icon
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.material_icon")


class MaterialIconSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        codepoint: str,
        size: int = 12,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        color_outline: Optional[Color] = None,
        font_name: str = "fonts/material-icons.ttf",
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.codepoint = codepoint
        self.size = size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.font_name = font_name
        self.render()

    def render(self) -> None:
        icon = render_material_icon(
            self.codepoint, self.size, self.color_fg, self.color_outline
        )
        self.image.fill(self.color_bg)
        self.image.blit(icon, (0, 0))
        self.dirty = 1
