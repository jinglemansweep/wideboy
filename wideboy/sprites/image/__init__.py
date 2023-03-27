import logging
import pygame
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.images import load_resize_image


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
        image = load_resize_image(self.filename, self.size)
        image.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = image
