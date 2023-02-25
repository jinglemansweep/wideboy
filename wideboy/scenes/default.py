import logging
import pygame

from wideboy.sprites import Act, Animation
from wideboy.sprites.image import ImageSprite
from wideboy.sprites.clock import ClockSprite
from wideboy.sprites.text import TextSprite
from wideboy.sprites.weather import WeatherSprite
from wideboy.scenes import BaseScene
from wideboy.utils.pygame import EVENT_EPOCH_MINUTE


logger = logging.getLogger(__name__)


class DefaultScene(BaseScene):
    def __init__(
        self, surface: pygame.surface.Surface, bg_color: pygame.color.Color = (0, 0, 0)
    ) -> None:
        super().__init__(surface, bg_color)
        # Setup background widget
        self.background_widget = ImageSprite(
            (
                0,
                self.height,
                self.width,
                self.height,
            ),
            (self.height * 2, self.height * 2),
            (self.width, self.height),
            255,
        )
        self.group.add(self.background_widget)
        # Setup clock widget
        self.clock_widget = ClockSprite(
            (
                self.width,
                0,
                128,
                self.height,
            ),
            color_bg=(32, 0, 32, 192),
        )
        self.group.add(self.clock_widget)
        # Setup weather widget
        self.weather_widget = WeatherSprite(
            (self.width - 256 + 4, self.height, 128 - 8, self.height - 8),
            (0, 0, 0, 192),
        )
        self.group.add(self.weather_widget)
        # Setup text widget
        self.text_widget = TextSprite((128 + 4, 0 - self.height, 512 - 8, 56))
        self.group.add(self.text_widget)
        # Set initial mode
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

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                self.change_mode("blank", 5)

    # Modes

    def handle_modes(self) -> None:
        if self.mode_next != self.mode:
            self.mode = self.mode_next
            logger.info(f"scene:handle_modes mode={self.mode}")
            if self.mode == "default":
                self._mode_default()
            elif self.mode == "blank":
                self._mode_blank()

    def _mode_default(self) -> None:
        self.act = Act(
            128,
            [
                (0, lambda: self.background_widget.set_random_image()),
                (0, lambda: self.text_widget.set_random_content()),
                (
                    0,
                    Animation(
                        self.background_widget,
                        (0, 0),
                        64,
                        (0, self.height),
                    ),
                ),
                (
                    32,
                    Animation(
                        self.clock_widget,
                        (self.width - 128, 0),
                        32,
                    ),
                ),
                (
                    64,
                    Animation(
                        self.weather_widget,
                        (self.width - 256 + 4, 4),
                        64,
                        (self.width - 256 + 4, self.height),
                    ),
                ),
                (
                    64,
                    Animation(
                        self.text_widget,
                        (4, 4),
                        64,
                        (4, 0 - self.height),
                    ),
                ),
            ],
        )
        self.act.start()

    def _mode_blank(self) -> None:
        self.act = Act(
            128,
            [
                (
                    0,
                    Animation(
                        self.text_widget,
                        (4, self.height),
                        32,
                        (4, 4),
                    ),
                ),
                (
                    0,
                    Animation(
                        self.weather_widget,
                        (self.width - 256 + 4, 0 - self.height),
                        32,
                    ),
                ),
                (
                    64,
                    Animation(
                        self.background_widget,
                        (0, self.height),
                        64,
                        (0, 0),
                    ),
                ),
            ],
        )
        self.act.start()
