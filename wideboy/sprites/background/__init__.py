import logging
import os
import pygame
import random
import yaml
from pygame import Clock, Color, Event, Rect, Surface, Vector2
from PIL import ImageFilter
from typing import Any, Optional
from wideboy.scenes.base import BaseScene
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
        scene: BaseScene,
        rect: Rect,
        alpha: int = 255,
        shuffle: bool = False,
    ) -> None:
        super().__init__(scene, rect)
        self.alpha = alpha
        self.glob_images(shuffle)
        self.image_index = random.randint(0, len(self.image_files) - 1)
        self.render_next_image()
        logger.debug(f"sprite:image files={len(self.image_files)}")

    def render_next_image(self):
        filename = self.image_files[self.image_index]
        logger.debug(f"image:next index={self.image_index} filename={filename}")
        surface = Surface((self.rect.width, self.rect.height))
        orig_image = load_image(filename)
        scaled_image = scale_surface(orig_image, (self.rect.width, self.rect.height))
        surface.blit(scaled_image, (0, 0))
        metadata = self.load_metadata(filename)
        if metadata:
            label_text = metadata["inputs"]["prompt"].strip()
            label = render_text(
                label_text,
                "fonts/bitstream-vera.ttf",
                10,
                color_fg=Color(255, 255, 0, 255),
                color_bg=Color(0, 0, 0, 128),
                color_outline=Color(0, 0, 0, 255),
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

    def load_metadata(self, filename: str) -> Any:
        basename, _ = os.path.splitext(filename)
        try:
            with open(f"{basename}.yml", "r") as yaml_file:
                return yaml.safe_load(yaml_file)
        except Exception as e:
            logger.warn(f"metadata:load error={e}")
        return None
