import logging
import pygame
from pygame import Color, Rect, Surface, SRCALPHA
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.placeholder")


class RectSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        color_bg: Color = (0, 0, 0, 192),
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.render()

    def render(self) -> None:
        self.image.fill(self.color_bg)
        self.dirty = 1
