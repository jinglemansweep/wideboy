from __future__ import annotations

import abc
import logging

import pygame

logger = logging.getLogger(__name__)


class Display(abc.ABC):
    def start(self) -> None:
        pass

    @abc.abstractmethod
    def present(self, surface: pygame.Surface) -> None: ...

    def stop(self) -> None:
        pass

    @staticmethod
    def surface_to_pil(surface: pygame.Surface):
        from PIL import Image

        pixels = pygame.image.tostring(surface, "RGB")
        return Image.frombytes("RGB", (surface.get_width(), surface.get_height()), pixels)
