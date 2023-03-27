import logging
import pygame
from enum import Enum
from typing import Optional
from wideboy.state import STATE

logger = logging.getLogger(__name__)


class SceneState(Enum):
    stopped = 0
    starting = 1
    started = 2
    stopping = 3


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
        self.state = SceneState.stopped
        self.setup()

    def reset(self) -> None:
        self.stop()
        self.setup()

    def setup(self) -> None:
        self.frame = 0

    def start(self) -> None:
        logger.debug(f"scene:state name={self.name} state=starting")
        self.state = SceneState.starting

    def stop(self) -> None:
        logger.debug(f"scene:state name={self.name} state=stopping")
        self.state = SceneState.stopping

    def destroy(self) -> None:
        logger.debug(f"scene:destroy name={self.name}")
        self.group.empty()

    def render(
        self,
        delta: float,
        events: list[pygame.event.Event],
    ) -> list[pygame.rect.Rect]:
        self.update(delta, events)
        self.clear()
        return self.draw()

    def clear(self) -> None:
        self.group.clear(self.surface, self.background)

    def update(self, delta: float, events: list[pygame.event.Event]) -> None:
        self.handle_state_change()
        self.handle_events(events)
        self.group.update(self.frame, delta, events)
        self.frame += 1

    def draw(self) -> list[pygame.rect.Rect]:
        return self.group.draw(self.surface)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass

    def handle_state_change(self) -> None:
        if self.state == SceneState.starting:
            self.state = SceneState.started
        if self.state == SceneState.stopping:
            self.state = SceneState.stopped
        if self.state == SceneState.stopped:
            self.destroy()

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


def build_background(
    size: pygame.math.Vector2, color: pygame.color.Color
) -> pygame.surface.Surface:
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
