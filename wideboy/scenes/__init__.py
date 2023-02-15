import pygame


class BaseScene:
    def __init__(self, surface: pygame.surface.Surface, background=None):
        self.surface = surface
        self.background = background
        self.group = pygame.sprite.LayeredDirty()

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


def build_background(size: tuple[int, int], color: pygame.color.Color):
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
