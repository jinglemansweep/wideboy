import logging
import pygame
import time

logger = logging.getLogger(__name__)


class BaseScene:
    def __init__(
        self, surface: pygame.surface.Surface, bg_color: pygame.color.Color
    ) -> None:
        self.surface = surface
        self.background = build_background(
            (surface.get_rect().width, surface.get_rect().height), bg_color
        )
        self.group = pygame.sprite.LayeredDirty()
        self.mode = None

    def render(
        self, frame: int, delta: float, events: list[pygame.event.Event]
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

    def change_mode(self, mode: str, timeout: int = 0) -> None:
        logger.info(f"scene:mode_change mode={mode} timeout={timeout}")
        self.mode_next = mode
        self.mode_timeout = timeout
        self.mode_changed = time.time()

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    def handle_mode_timeout(self) -> None:
        # if mode timeout is set, and timeout has elapsed, reset to "default" mode
        if (
            self.mode_timeout > 0
            and time.time() > self.mode_changed + self.mode_timeout
        ):
            self.change_mode("default")


def build_background(
    size: tuple[int, int], color: pygame.color.Color
) -> pygame.surface.Surface:
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
