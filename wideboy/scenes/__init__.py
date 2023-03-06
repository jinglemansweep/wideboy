import logging
import pygame
import time

from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)


class BaseScene:
    def __init__(
        self,
        surface: pygame.surface.Surface,
        state: StateStore,
        bg_color: pygame.color.Color,
    ) -> None:
        self.surface = surface
        self.state = state
        self.background = build_background(
            (surface.get_rect().width, surface.get_rect().height), bg_color
        )
        self.group = pygame.sprite.LayeredDirty()

    def render(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        self.update(frame, delta, events)
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.surface, self.background)

    def update(
        self, frame: int, delta: float, events: list[pygame.event.Event]
    ) -> None:
        self.handle_events(events)
        self.group.update(frame, delta, events)

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.surface)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    @property
    def height(self):
        return self.surface.get_rect().height

    @property
    def width(self):
        return self.surface.get_rect().width


def build_background(
    size: tuple[int, int], color: pygame.color.Color
) -> pygame.surface.Surface:
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
