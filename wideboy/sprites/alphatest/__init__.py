import logging
import pygame
from pygame import SRCALPHA
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.placeholder")


class AlphaSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (255, 255, 255, 255),
        alpha: int = 255,
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.alpha = alpha
        self.draw()

    def update(
        self,
        frame: str,
        clock: pygame.time.Clock,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        val = frame % 64
        self.alpha = val * 4
        self.draw()

    def draw(self) -> None:
        self.image.fill(self.color_bg)
        self.image.set_alpha(self.alpha)
        self.dirty = 1
