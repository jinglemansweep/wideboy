import logging
from pygame import Color, Rect, Surface, SRCALPHA
from wideboy.sprites.image_helpers import render_text
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.text")


class TextSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        text: str,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 20,
        color_fg: Color = (255, 255, 255, 255),
        color_bg: Color = (0, 0, 0, 255),
        color_outline: Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.render()

    def set_text(self, text: str) -> None:
        self.text = text
        self.render()

    def render(self) -> None:
        text_surface = render_text(
            self.text,
            self.font_name,
            self.font_size,
            self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.fill(self.color_bg)
        self.image.blit(text_surface, (0, 0))
        self.dirty = 1
