import logging
import pygame
import random
import schedule

from wideboy.sprites.clock import ClockWidgetSprite
from wideboy.scenes import BaseScene, build_background


logger = logging.getLogger(__name__)


class DefaultScene(BaseScene):
    def __init__(
        self, surface: pygame.surface.Surface, bg_color: pygame.color.Color = (0, 0, 0)
    ) -> None:
        super().__init__(surface)
        self.background = build_background(
            (surface.get_rect().width, surface.get_rect().height), bg_color
        )
        self.clock_visible = True
        self.clock_widget = ClockWidgetSprite(
            (
                self.surface.get_rect().width - 128,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(128, 0, 0, 255),
        )
        self.group.add(self.clock_widget)
        schedule.every(10).seconds.do(self.toggle_clock_visibility)

    def toggle_clock_visibility(self):
        if self.clock_visible:
            # hide clock
            self.clock_widget.mover.move((0, 0), 50)
            self.clock_visible = False
        else:
            # show clock
            self.clock_widget.mover.move((self.surface.get_rect().width - 128, 0), 50)
            self.clock_visible = True
        logger.info(f"clock:toggle visible={self.clock_visible}")

    def update(self, frame, delta) -> None:
        super().update(frame, delta)
        schedule.run_pending()
        """
        if frame % 200 == 0:
            self.clock1_widget.mover.move(
                (random.randint(0, 640), 0),
                50,
            )
        """
