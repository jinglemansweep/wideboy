import logging
import pygame

from wideboy.sprites.image_helpers import build_background
from wideboy.state import STATE

logger = logging.getLogger("scenes.base")


class BaseScene:
    name: str
    frame: int
    debug_every_frame: int = 1000

    def __init__(
        self,
        surface: pygame.surface.Surface,
        bg_color: pygame.color.Color,
    ) -> None:
        self.surface = surface
        self.background = build_background(
            pygame.math.Vector2(surface.get_rect().width, surface.get_rect().height),
            bg_color,
        )
        self.group = pygame.sprite.LayeredDirty()
        self.setup()

    def reset(self) -> None:
        self.destroy()
        self.setup()

    def setup(self) -> None:
        self.frame = 0

    def destroy(self) -> None:
        logger.debug(f"scene:destroy name={self.name}")
        self.clear()
        self.group.empty()
        self.surface.blit(self.background, (0, 0))

    def draw(
        self,
        clock: pygame.time.Clock,
        delta: float,
        events: list[pygame.event.Event],
    ) -> list[pygame.rect.Rect]:
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.surface, self.background)

    def update(
        self, clock: pygame.time.Clock, delta: float, events: list[pygame.event.Event]
    ) -> None:
        self.handle_events(events)
        self.group.update(self.frame, clock, delta, events)
        self.frame += 1

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.surface)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    def debug(self, clock: pygame.time.Clock, delta: float) -> None:
        frame = self.frame
        if frame % self.debug_every_frame == 0:
            logger.debug(
                f"scene:debug frame={frame} fps={clock.get_fps()} delta={delta} state={STATE}"
            )

    @property
    def height(self):
        return self.surface.get_rect().height

    @property
    def width(self):
        return self.surface.get_rect().width
