import logging
import pygame

from wideboy.sprites import BaseSprite
from wideboy.utils.images import load_resize_image, tile_surface


logger = logging.getLogger("sprites.background")


class ImageSprite(BaseSprite):
    def __init__(
        self,
        filename: str,
        rect: pygame.Rect,
        tile_size: tuple[int, int],
        fill_size: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        super().__init__(rect)
        image = load_resize_image(filename, tile_size)
        image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = tile_surface(image, fill_size)

    def update(self, frame: int, delta: float) -> None:
        super().update(frame, delta)
