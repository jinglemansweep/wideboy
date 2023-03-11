import logging
import pygame
import random
from typing import Optional

from wideboy.sprites import BaseSprite
from wideboy.utils.images import glob_files, load_resize_image, tile_surface
from wideboy.utils.state import StateStore


logger = logging.getLogger("sprites.background")


class ImageSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        state: StateStore,
        tile_size: tuple[int, int],
        fill_size: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        super().__init__(rect, state)
        self.tile_size = tile_size
        self.fill_size = fill_size
        self.alpha = alpha
        self.files = self.glob_images()
        self.set_random_image()
        self.dirty = 2
        logger.debug(f"sprite:image files={len(self.files)}")

    def set_random_image(self):
        filename = random.choice(self.files)
        tile_size = random.randint(64 * 2, 64 * 8)
        self.image = self.load_image(filename, tile_size=(tile_size, tile_size))

    def glob_images(self):
        return glob_files("images/backgrounds", "*.png")

    def load_image(
        self,
        filename: str,
        tile_size: Optional[tuple[int, int]] = None,
        fill_size: Optional[tuple[int, int]] = None,
        alpha: Optional[int] = None,
    ):
        tile_size = tile_size or self.tile_size
        fill_size = fill_size or self.fill_size
        alpha = alpha or self.alpha
        logger.debug(
            f"sprite:image:load filename={filename} tile_size={tile_size} fill_size={fill_size} alpha={alpha}"
        )
        image = load_resize_image(filename, tile_size)
        image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        return tile_surface(image, fill_size)

    def update(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
