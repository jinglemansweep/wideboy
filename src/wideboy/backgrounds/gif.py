from __future__ import annotations

import logging
from typing import Any

import pygame
from PIL import Image, ImageSequence

from .base import Background

logger = logging.getLogger(__name__)


class GifBackground(Background):
    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        super().__init__(settings)
        self._frames: list[pygame.Surface] = []
        self._durations: list[float] = []
        self._frame_index = 0
        self._elapsed = 0.0
        path = (settings or {}).get("path")
        if path:
            self._load(path)

    def _load(self, path: str) -> None:
        try:
            gif = Image.open(path)
            for frame in ImageSequence.Iterator(gif):
                duration = frame.info.get("duration", 100) / 1000.0
                self._durations.append(duration)
                rgba = frame.convert("RGBA")
                surf = pygame.image.fromstring(rgba.tobytes(), rgba.size, "RGBA")
                self._frames.append(surf.convert_alpha())
            logger.info("Loaded %d frames from %s", len(self._frames), path)
        except Exception:
            logger.exception("Failed to load GIF: %s", path)

    def update(self, dt: float) -> None:
        if not self._frames:
            return
        self._elapsed += dt
        while self._elapsed >= self._durations[self._frame_index]:
            self._elapsed -= self._durations[self._frame_index]
            self._frame_index = (self._frame_index + 1) % len(self._frames)

    def render(self, surface: pygame.Surface) -> None:
        if not self._frames:
            return
        frame = self._frames[self._frame_index]
        scaled = pygame.transform.smoothscale(frame, surface.get_size())
        surface.blit(scaled, (0, 0))
