import logging
import os
import pygame
import random

from PIL import ImageFilter
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.images import (
    glob_files,
    load_transform_image,
    apply_surface_filter,
    render_text,
)
from wideboy.config import settings

logger = logging.getLogger("sprites.background")


class BackgroundSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        size: pygame.math.Vector2,
        alpha: int = 255,
    ) -> None:
        super().__init__(rect)
        self.size = size
        self.alpha = alpha
        self.image_index = 0
        self.glob_images()
        self.render_next_image()
        logger.debug(f"sprite:image files={len(self.image_files)}")

    def render_next_image(self):
        filename = self.image_files[self.image_index]
        logger.debug(f"image:next index={self.image_index} filename={filename}")
        surface = pygame.surface.Surface(self.size)
        file_image = self.load_image(filename, self.size)
        file_image_blurred = apply_surface_filter(
            pygame.transform.scale(file_image, self.size), ImageFilter.BLUR
        )
        surface.blit(file_image_blurred, (0, 0))
        surface.blit(file_image, (0, 0))
        label_text = (
            os.path.splitext(os.path.basename(filename))[0].replace("t_", "").upper()
        )
        label = render_text(
            label_text, "fonts/bitstream-vera.ttf", 10, pygame.Color(255, 255, 0)
        )
        surface.blit(label, (0, self.rect.height - 14))
        self.image = surface
        self.image_index += 1
        if self.image_index > len(self.image_files) - 1:
            self.image_index = 0
        self.dirty = 1

    def glob_images(self, shuffle: bool = False):
        self.image_files = glob_files(
            os.path.join(settings.paths.images_backgrounds), "*.png"
        )
        if shuffle:
            random.shuffle(self.image_files)
        if self.image_index > len(self.image_files) - 1:
            self.image_index = 0

    def load_image(
        self,
        filename: str,
        size: Optional[pygame.math.Vector2] = None,
        alpha: Optional[int] = 255,
        blur: Optional[bool] = False,
    ):
        logger.debug(
            f"image:load filename={filename} size={size} alpha={alpha} blur={blur}"
        )
        image = load_transform_image(filename, size, blur)
        image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        return image

    def update(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
