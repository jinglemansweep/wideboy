from __future__ import annotations

import logging
from typing import Any

import pygame

from ..render.image import load_image
from .base import Background

logger = logging.getLogger(__name__)


class ImageBackground(Background):
    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        super().__init__(settings)
        self._image: pygame.Surface | None = None
        path = (settings or {}).get("path")
        if path:
            self._load(path)

    def _load(self, path: str) -> None:
        try:
            self._image = load_image(path)
        except Exception:
            logger.exception("Failed to load background image: %s", path)

    def render(self, surface: pygame.Surface) -> None:
        if self._image is not None:
            scaled = pygame.transform.smoothscale(self._image, surface.get_size())
            surface.blit(scaled, (0, 0))
