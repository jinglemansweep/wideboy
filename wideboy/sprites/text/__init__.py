import logging
import pygame
import random
from pygame import SRCALPHA
from wideboy.sprites.images import render_text
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger(__name__)


class TextSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        text: str,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 20,
        color_fg: pygame.color.Color = (255, 255, 255, 255),
        color_outline: pygame.color.Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.render()

    def render(self) -> None:
        text_surface = render_text(
            self.text,
            self.font_name,
            self.font_size,
            self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(text_surface, (0, 0))
        self.dirty = 1
