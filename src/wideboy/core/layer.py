from __future__ import annotations

import abc

import pygame


class Layer(abc.ABC):
    def __init__(
        self,
        position: tuple[int, int] = (0, 0),
        z_order: int = 0,
        visible: bool = True,
    ) -> None:
        self.position = position
        self.z_order = z_order
        self.visible = visible
        self._cached_surface: pygame.Surface | None = None
        self._dirty = True

    def mark_dirty(self) -> None:
        self._dirty = True

    def update(self, dt: float) -> None:
        pass

    @abc.abstractmethod
    def _render(self, surface: pygame.Surface) -> None: ...

    def _surface_size(self) -> tuple[int, int] | None:
        return None

    def render(self, target: pygame.Surface, brightness: float = 1.0) -> None:
        if not self.visible:
            return
        if self._dirty or self._cached_surface is None:
            size = self._surface_size() or target.get_size()
            if self._cached_surface is None or self._cached_surface.get_size() != size:
                self._cached_surface = pygame.Surface(size, pygame.SRCALPHA)
            else:
                self._cached_surface.fill((0, 0, 0, 0))
            self._render(self._cached_surface)
            self._dirty = False
        if brightness < 1.0:
            self._cached_surface.set_alpha(int(255 * brightness))
        else:
            self._cached_surface.set_alpha(255)
        target.blit(self._cached_surface, self.position)
