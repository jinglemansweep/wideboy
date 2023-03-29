import logging
import os
import pygame
import random
import yaml

from PIL import ImageFilter
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    glob_files,
    load_image,
    apply_filters,
    render_text,
    pil_to_surface,
)
from wideboy.config import settings

logger = logging.getLogger("sprite.background")


class BackgroundSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        size: pygame.math.Vector2,
        alpha: int = 255,
        shuffle: bool = False,
    ) -> None:
        super().__init__(rect)
        self.size = size
        self.alpha = alpha
        self.glob_images(shuffle)
        self.image_index = random.randint(0, len(self.image_files) - 1)
        self.render_next_image()
        logger.debug(f"sprite:image files={len(self.image_files)}")

    def render_next_image(self):
        filename = self.image_files[self.image_index]
        logger.debug(f"image:next index={self.image_index} filename={filename}")
        surface = pygame.surface.Surface(self.size)
        orig_image = load_image(filename)
        orig_image = pygame.transform.scale(orig_image, (512, 64))
        blurred_image = apply_filters(
            pygame.transform.scale(orig_image.copy(), self.size),
            alpha=192,
            filters=[ImageFilter.BLUR],
        )
        surface.blit(blurred_image, (0, 0))
        surface.blit(orig_image, (128, 0))
        metadata = self.load_metadata(filename)
        if metadata:
            label_text = metadata["inputs"]["prompt"].strip()
            label = render_text(
                label_text,
                "fonts/bitstream-vera.ttf",
                11,
                pygame.Color(255, 255, 0),
                pygame.Color(0, 0, 0, 192),
                pygame.Color(0, 0, 0, 0),
            )
            surface.blit(label, (640 - label.get_width(), self.rect.height - 15))
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

    def load_metadata(self, filename: str) -> dict:
        basename, _ = os.path.splitext(filename)
        try:
            with open(f"{basename}.yml", "r") as yaml_file:
                return yaml.safe_load(yaml_file)
        except Exception as e:
            logger.warn(f"metadata:load error={e}")
        return None

    def update(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
