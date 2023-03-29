import logging
import pygame
from pygame import SRCALPHA
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.placeholder")


class PlaceholderSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 192),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.draw()

    def draw(self) -> None:
        self.image.fill(self.color_bg)
        self.dirty = 1
