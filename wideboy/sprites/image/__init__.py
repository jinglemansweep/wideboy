import logging
import os
import pygame
import random
from typing import Optional

from wideboy.sprites._base import BaseSprite
from wideboy.utils.images import glob_files, load_resize_image, tile_surface
from wideboy.utils.state import StateStore

logger = logging.getLogger("sprites.background")


class ImageSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        state: StateStore,
        image_path: str,
        tile_size: tuple[int, int],
        fill_size: tuple[int, int],
        alpha: int = 255,
    ) -> None:
        super().__init__(rect, state)
        self.image_path = image_path
        self.tile_size = tile_size
        self.fill_size = fill_size
        self.alpha = alpha
        self.image_index = 0
        self.glob_images(True)
        self.render_next_image()
        self.dirty = 2
        logger.debug(f"sprite:image files={len(self.image_files)}")

    def render_next_image(self):
        filename = self.image_files[self.image_index]
        tile_size = random.randint(64 * 2, 64 * 8)
        logger.debug(
            f"sprite:image:next index={self.image_index} filename={filename} tile_size={tile_size}"
        )
        self.image = self.load_image(filename, tile_size=(tile_size, tile_size))
        self.image_index += 1
        if self.image_index > len(self.image_files) - 1:
            self.image_index = 0

    def glob_images(self, shuffle: bool = False):
        self.image_files = glob_files(
            os.path.join(self.image_path, "backgrounds"), "*.png"
        )
        if shuffle:
            random.shuffle(self.image_files)
        if self.image_index > len(self.image_files) - 1:
            self.image_index = 0

    def load_image(
        self,
        filename: str,
        tile_size: Optional[tuple[int, int]] = None,
        fill_size: Optional[tuple[int, int]] = None,
        alpha: Optional[int] = None,
    ):
        is_tiled = os.path.basename(filename).startswith("t_")
        tile_size = tile_size or self.tile_size
        fill_size = fill_size or self.fill_size
        alpha = alpha or self.alpha
        logger.debug(
            f"sprite:image:load filename={filename} is_tiled={is_tiled} tile_size={tile_size} fill_size={fill_size} alpha={alpha}"
        )
        image = load_resize_image(filename, tile_size if is_tiled else fill_size)
        image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        if is_tiled:
            image = tile_surface(image, fill_size)
        return image

    def update(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
