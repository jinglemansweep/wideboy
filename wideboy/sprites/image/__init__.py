import logging
import pygame
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    load_image,
    apply_filters,
)


logger = logging.getLogger(__name__)


class ImageSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        size: Optional[pygame.math.Vector2],
        filename: str,
        alpha: int = 255,
    ) -> None:
        super().__init__(rect)
        self.filename = filename
        self.size = size
        self.alpha = alpha
        self.render()

    def render(self) -> None:
        surface = load_image(self.filename)
        self.rect = surface.get_rect()
        surface = pygame.transform.scale(surface, self.size)
        surface = apply_filters(surface, alpha=self.alpha)
        self.image = surface
        self.dirty = 1
