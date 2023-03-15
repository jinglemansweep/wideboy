import logging
import pygame

from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)


class BaseScene:
    name: str = None
    frame: int = None
    debug_every_frame: int = 1000

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
        self.setup()

    def setup(self) -> None:
        self.frame = 0

    def render(
        self,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        self.update(delta, events)
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.surface, self.background)

    def update(self, delta: float, events: list[pygame.event.Event]) -> None:
        self.handle_events(events)
        self.group.update(self.frame, delta, events)
        self.frame += 1

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.surface)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    def debug(
        self, frame: int, clock: pygame.time.Clock, delta: float, state: StateStore
    ) -> None:
        if frame % self.debug_every_frame == 0:
            logger.debug(
                f"scene:debug frame={frame} fps={clock.get_fps()} delta={delta} state={state}"
            )

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
