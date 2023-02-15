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
        self.clock1_widget = ClockWidgetSprite(
            (
                self.surface.get_rect().width - 128,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(128, 0, 0, 255),
        )
        self.group.add(self.clock1_widget)

        self.clock2_widget = ClockWidgetSprite(
            (
                320,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(0, 0, 128, 255),
        )
        self.group.add(self.clock2_widget)

        self.clock3_widget = ClockWidgetSprite(
            (
                0,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(0, 128, 0, 255),
        )
        self.group.add(self.clock3_widget)

    def update(self, frame, delta) -> None:
        super().update(frame, delta)
        if frame % 200 == 0:
            self.clock1_widget.mover.move(
                (random.randint(0, 640), 0),
                50,
            )
        if frame % 300 == 0:
            self.clock2_widget.mover.move(
                (random.randint(0, 640), 0),
                100,
            )
        if frame % 350 == 0:
            self.clock3_widget.mover.move(
                (random.randint(0, 640), 0),
                200,
            )
