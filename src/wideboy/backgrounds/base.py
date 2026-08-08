from __future__ import annotations

import abc
from typing import Any

import pygame


class Background(abc.ABC):
    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        self.settings = settings or {}

    def update(self, dt: float) -> None:
        pass

    @abc.abstractmethod
    def render(self, surface: pygame.Surface) -> None: ...
