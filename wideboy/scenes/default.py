import logging
import pygame

from wideboy.sprites import Act, Animation
from wideboy.sprites.image import ImageSprite
from wideboy.sprites.clock import ClockSprite
from wideboy.scenes import BaseScene, build_background
from wideboy.utils.pygame import EVENT_EPOCH_MINUTE


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
            (surface.get_rect().height * 2, surface.get_rect().height * 2),
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
        self.change_mode("default")

    def update(
        self, frame: int, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)
        self.handle_mode_timeout()
        self.handle_modes()
        if self.act is not None:
            self.act.update()

    # Handle Events

    def handle_events(self, events: list[pygame.event.Event]):
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                self.change_mode("blank", 5)

    # Modes

    def handle_modes(self):
        if self.mode_next != self.mode:
            self.mode = self.mode_next
            logger.info(f"scene:handle_modes mode={self.mode}")
            if self.mode == "default":
                self._mode_default()
            elif self.mode == "blank":
                self._mode_blank()

    def _mode_default(self):
        self.act = Act(
            100,
            [
                (0, lambda: self.background_widget.set_random_image()),
                (
                    0,
                    Animation(
                        self.clock_widget,
                        (self.surface.get_rect().width - 128, 0),
                        100,
                    ),
                ),
                (
                    0,
                    Animation(
                        self.background_widget,
                        (0, 0),
                        100,
                        (0, self.surface.get_rect().height),
                    ),
                ),
            ],
        )
        self.act.start()

    def _mode_blank(self):
        self.act = Act(
            100,
            [
                (
                    0,
                    Animation(
                        self.clock_widget,
                        (0, 0),
                        100,
                    ),
                ),
                (
                    0,
                    Animation(
                        self.background_widget,
                        (0, self.surface.get_rect().height),
                        100,
                        (0, 0),
                    ),
                ),
            ],
        )
        self.act.start()
