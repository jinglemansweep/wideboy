import logging
import os
import pygame
import random
import yaml
from pygame import Clock, Color, Event, Rect, Surface, Vector2
from PIL import ImageFilter
from typing import Optional
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    glob_files,
    load_image,
    filter_surface,
    scale_surface,
    render_text,
)
from wideboy.config import settings

logger = logging.getLogger("sprite.background")


class BackgroundSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        size: Vector2,
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
        surface = Surface(self.size)
        orig_image = load_image(filename)
        orig_image = pygame.transform.scale(orig_image, (512, 64))
        blurred_image = filter_surface(
            scale_surface(orig_image.copy(), self.size),
            alpha=192,
            filters=[ImageFilter.BLUR],
        )
        surface.blit(blurred_image, (0, 0))
        surface.blit(orig_image, (0, 0))
        metadata = self.load_metadata(filename)
        if metadata:
            label_text = metadata["inputs"]["prompt"].strip()
            label = render_text(
                label_text,
                "fonts/bitstream-vera.ttf",
                11,
                color_fg=Color(255, 255, 0, 255),
                color_bg=Color(0, 0, 0, 192),
                color_outline=Color(0, 0, 0, 255),
            )
            surface.blit(label, (512 - label.get_width(), self.rect.height - 15))
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
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
