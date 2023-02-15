import pygame
import time


class BaseScene:
    def __init__(self, surface: pygame.surface.Surface, bg_color: pygame.color.Color):
        self.surface = surface
        self.background = build_background(
            (surface.get_rect().width, surface.get_rect().height), bg_color
        )
        self.group = pygame.sprite.LayeredDirty()
        self.mode = None
        self.mode_next = None

    def render(self, frame: int, delta: float) -> None:
        self.update(frame, delta)
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.surface, self.background)

    def update(self, frame: int, delta: float) -> None:
        self.group.update(frame, delta)

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.surface)

    def change_mode(self, mode: str):
        self.mode_next = mode


def build_background(size: tuple[int, int], color: pygame.color.Color):
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
