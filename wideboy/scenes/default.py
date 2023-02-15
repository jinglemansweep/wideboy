import pygame
import random

from wideboy.sprites.clock import ClockWidgetSprite
from wideboy.scenes import BaseScene, build_background


class DefaultScene(BaseScene):
    def __init__(
        self, surface: pygame.surface.Surface, bg_color: pygame.color.Color = (0, 0, 0)
    ) -> None:
        super().__init__(surface)
        self.background = build_background(
            (surface.get_rect().width, surface.get_rect().height), bg_color
        )
        self.actors = {
            "clock": ClockWidgetSprite(
                (
                    self.surface.get_rect().width - 128,
                    0,
                    128,
                    self.surface.get_rect().height,
                ),
                color_bg=(128, 0, 0, 255),
            )
        }
        self.group.add(self.actors["clock"])

    def update(self, frame, delta) -> None:
        super().update(frame, delta)
        clock = self.actors["clock"]
        if frame % 200 == 0:
            clock.mover.move(
                (clock.rect[0], clock.rect[1]),
                (random.randint(0, 640), 0),
                100,
            )

        clock.mover.tick()
        if clock.mover.is_moving():
            clock.rect.x, clock.rect.y = clock.mover.current
            clock.dirty = 1

        """
        print("UPDATE")
        self.actors["clock"].rect.y += 1
        self.actors["clock"].dirty = 1
        """
