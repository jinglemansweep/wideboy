import logging
import os

import random
import yaml
from pygame import Clock, Color, Event, Rect, Surface
from typing import Any
from wideboy.constants import EVENT_NIGHT_MODE
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.animation_helpers import Animator, AnimatorState
from wideboy.sprites.image_helpers import (
    glob_files,
    load_image,
    scale_surface,
    render_text,
)

logger = logging.getLogger("sprite.background")


class BackgroundSprite(BaseSprite):
    alpha_animator: Animator
    night_mode = False

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        image_path: str,
        shuffle: bool = False,
    ) -> None:
        super().__init__(scene, rect)
        self.image_path = image_path
        self.alpha_animator = Animator(range=(0.0, 255.0), open=True, speed=4.0)
        self.glob_images(self.image_path, shuffle)
        self.image_index = random.randint(0, len(self.image_files) - 1)
        self.render_next_image()
        logger.debug(f"sprite:image files={len(self.image_files)}")

    def update(
        self,
        frame: int,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if event.type == EVENT_NIGHT_MODE:
                self.night_mode = event.payload == "ON"
                self.dirty = 1
        self.alpha_animator.update()
        if self.alpha_animator.state == AnimatorState.CLOSED:
            self.render_next_image()
            self.alpha_animator.set(True)
        if self.image:
            self.image.set_alpha(
                64 if self.night_mode else int(self.alpha_animator.value)
            )
        if self.alpha_animator.animating:
            self.dirty = 1
        # logger.debug(f"image:update alpha_animator={self.alpha_animator.value}")

    def change_image(self):
        if self.alpha_animator.state == AnimatorState.OPEN:
            self.alpha_animator.set(False)

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

    def glob_images(self, image_path: str, shuffle: bool = False):
        self.image_files = glob_files(image_path, "*.png")
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
