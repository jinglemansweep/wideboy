import logging
import pygame
import random
import schedule
import time

from wideboy.sprites import Act, Animation
from wideboy.sprites.image import ImageSprite
from wideboy.sprites.clock import ClockSprite
from wideboy.scenes import BaseScene, build_background


logger = logging.getLogger(__name__)


class DefaultScene(BaseScene):
    def __init__(
        self, surface: pygame.surface.Surface, bg_color: pygame.color.Color = (0, 0, 0)
    ) -> None:
        super().__init__(surface, bg_color)
        # Setup background widget
        self.background_widget = ImageSprite(
            "images/backgrounds/mandms.png",
            (
                0,
                surface.get_rect().height,
                surface.get_rect().width,
                surface.get_rect().height,
            ),
            (surface.get_rect().height * 4, surface.get_rect().height * 4),
            (surface.get_rect().width, surface.get_rect().height),
            255,
        )
        self.group.add(self.background_widget)
        # Setup clock widget
        self.clock_widget = ClockSprite(
            (
                self.surface.get_rect().width,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(128, 0, 0, 255),
        )
        self.group.add(self.clock_widget)
        # Schedule some test events
        schedule.every(30).seconds.do(self.change_mode, mode="blank", timeout=5)
        self.change_mode("default")
        self.act = Act(
            300,
            [
                (
                    0,
                    Animation(
                        self.clock_widget,
                        (self.surface.get_rect().width - 128, 0),
                        64,
                        (0, 0),
                    ),
                ),
                (
                    100,
                    Animation(
                        self.clock_widget,
                        (0, 0),
                        64,
                        (self.surface.get_rect().width - 128, 0),
                    ),
                ),
            ],
            True,
        )
        self.act.run()

    def update(
        self, frame: int, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)
        schedule.run_pending()
        # self.handle_mode_timeout()
        # self.handle_modes()
        self.act.update()

    # Modes

    def handle_modes(self):
        if self.mode_next != self.mode:
            self.mode = self.mode_next
            logger.info(f"scene:handle_modes mode={self.mode}")
            if self.mode == "default":
                self._background_show()
                self._clock_show()
            elif self.mode == "blank":
                self._background_hide()
                self._clock_hide()

    # Background widget actions

    def _background_hide(self):
        self.background_widget.mover.move((0, self.surface.get_rect().height), 50)

    def _background_show(self):
        self.background_widget.mover.move((0, 0), 50)

    # Clock widget actions

    def _clock_hide(self):
        self.clock_widget.mover.move((0, 0), 50)

    def _clock_show(self):
        self.clock_widget.mover.move((self.surface.get_rect().width - 128, 0), 50)
