import logging
import pygame
import random
import schedule

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
        self.background_visible = True
        self.background_widget = ImageSprite(
            "images/backgrounds/mandms.png",
            (0, 0, surface.get_rect().width, surface.get_rect().height),
            (surface.get_rect().height * 4, surface.get_rect().height * 4),
            (surface.get_rect().width, surface.get_rect().height),
            255,
        )
        self.group.add(self.background_widget)
        # Setup clock widget
        self.clock_visible = True
        self.clock_widget = ClockSprite(
            (
                self.surface.get_rect().width - 128,
                0,
                128,
                self.surface.get_rect().height,
            ),
            color_bg=(128, 0, 0, 255),
        )
        self.group.add(self.clock_widget)
        # Schedule some test events
        schedule.every(15).seconds.do(self._background_toggle)
        schedule.every(10).seconds.do(self._clock_toggle)

    def update(self, frame, delta) -> None:
        super().update(frame, delta)
        schedule.run_pending()

    # Background widget actions

    def _background_hide(self):
        self.background_widget.mover.move((0, self.surface.get_rect().height), 50)
        self.background_visible = False

    def _background_show(self):
        self.background_widget.mover.move((0, 0), 50)
        self.background_visible = True

    def _background_toggle(self):
        if self.background_visible:
            self._background_hide()
        else:
            self._background_show()

    # Clock widget actions

    def _clock_toggle(self):
        if self.clock_visible:
            self._clock_hide()
        else:
            self._clock_show()

    def _clock_hide(self):
        self.clock_widget.mover.move((0, 0), 50)
        self.clock_visible = False

    def _clock_show(self):
        self.clock_widget.mover.move((self.surface.get_rect().width - 128, 0), 50)
        self.clock_visible = True
