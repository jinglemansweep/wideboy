from __future__ import annotations

import logging
import random
from enum import Enum
from pathlib import Path
from typing import Any

import pygame

from ..render.image import load_image
from .base import Background

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


class Transition(Enum):
    NONE = "none"
    FADE = "fade"
    WIPE = "wipe"
    FOLD = "fold"
    BLEED = "bleed"


class SlideshowBackground(Background):
    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        super().__init__(settings)
        s = settings or {}
        self.path = s.get("path", "assets/backgrounds")
        self.interval = float(s.get("interval", 60))
        self.transition = Transition(s.get("transition", "fade"))
        self.transition_speed = int(s.get("transition_speed", 8))

        self._images: list[pygame.Surface] = []
        self._current: pygame.Surface | None = None
        self._next: pygame.Surface | None = None
        self._elapsed = 0.0
        self._transitioning = False
        self._transition_progress = 0
        self._transition_state: dict[str, Any] = {}
        self._load_images()

    def _load_images(self) -> None:
        p = Path(self.path)
        if not p.is_dir():
            logger.warning("Background directory not found: %s", self.path)
            return
        for f in sorted(p.iterdir()):
            if f.suffix.lower() in IMAGE_EXTENSIONS:
                try:
                    img = load_image(str(f))
                    self._images.append(img)
                except Exception:
                    logger.warning("Failed to load %s", f)
        if self._images:
            self._current = self._images[0]
        logger.info("Loaded %d background images from %s", len(self._images), self.path)

    def update(self, dt: float) -> None:
        if not self._images:
            return
        if self._transitioning:
            self._transition_progress += 1
            if self._transition_progress > 50:
                self._current = self._next
                self._next = None
                self._transitioning = False
                self._transition_progress = 0
                self._transition_state = {}
            return
        self._elapsed += dt
        if self._elapsed >= self.interval:
            self._elapsed = 0.0
            self._next = random.choice(self._images)
            self._transitioning = True
            self._transition_progress = 0

    def render(self, surface: pygame.Surface) -> None:
        if self._current is not None:
            scaled = pygame.transform.smoothscale(self._current, surface.get_size())
            surface.blit(scaled, (0, 0))
        if self._transitioning and self._next is not None:
            next_scaled = pygame.transform.smoothscale(self._next, surface.get_size())
            if self.transition == Transition.FADE:
                alpha = int(255 * self._transition_progress / 50)
                next_scaled.set_alpha(alpha)
                surface.blit(next_scaled, (0, 0))
            elif self.transition == Transition.WIPE:
                w = surface.get_width()
                progress = int(w * self._transition_progress / 50)
                surface.blit(next_scaled, (0, 0), (0, 0, progress, surface.get_height()))
            else:
                alpha = int(255 * self._transition_progress / 50)
                next_scaled.set_alpha(alpha)
                surface.blit(next_scaled, (0, 0))
