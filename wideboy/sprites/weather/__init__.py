import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.sprites import BaseSprite


logger = logging.getLogger(__name__)


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 255),
        color_fg: pygame.color.Color = (255, 255, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.render()
        self.dirty = 2

    def update(
        self, frame: str, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)

    def render(self) -> None:
        self.image.fill(self.color_bg)
