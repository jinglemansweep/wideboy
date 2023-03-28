import logging
import pygame
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import load_image, scale_image, apply_filters


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
        image = scale_image(load_image(self.filename), self.size)
        image = apply_filters(image, alpha=self.alpha / 255)
        self.image = image
        self.dirty = 1
