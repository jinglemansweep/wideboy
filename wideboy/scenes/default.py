import logging
import pygame

from wideboy.sprites import Act, Animation
from wideboy.sprites.image import ImageSprite
from wideboy.sprites.clock import ClockSprite
from wideboy.sprites.text import TextSprite
from wideboy.sprites.weather import WeatherSprite
from wideboy.scenes import BaseScene
from wideboy.utils.pygame import EVENT_EPOCH_MINUTE, EVENT_EPOCH_SECOND
from wideboy.utils.state import StateStore


logger = logging.getLogger(__name__)


class DefaultScene(BaseScene):
    def __init__(
        self,
        surface: pygame.surface.Surface,
        state: StateStore,
        bg_color: pygame.color.Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, state, bg_color)
        # Setup background widget
        self.background_widget = ImageSprite(
            (
                0,
                0 - self.height,
                self.width,
                self.height,
            ),
            self.state,
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
            self.state,
            color_bg=(0, 64, 0, 192),
        )
        self.group.add(self.clock_widget)
        # Setup weather widget
        self.weather_widget = WeatherSprite(
            (self.width - 192, 32, 64, 64), self.state, color_bg=(0, 0, 64, 192)
        )
        self.group.add(self.weather_widget)
        # Setup text widget
        self.text_widget = TextSprite((4, self.height, 512 - 8, 56), self.state)
        self.group.add(self.text_widget)
        # Run initial acts
        self.act_clock_show = self.build_clock_show_act()
        self.act_clock_show.start()
        self.act_weather_show = self.build_weather_show_act()
        self.act_weather_show.start()
        self.act_background_change = self.build_background_change_act()
        self.act_background_change.start()
        self.act_ticker_change = self.build_ticker_change_act()
        self.act_ticker_change.start()

    def update(
        self,
        frame: int,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
        if self.act_clock_show is not None:
            self.act_clock_show.update()
        if self.act_weather_show is not None:
            self.act_weather_show.update()
        if self.act_background_change is not None:
            self.act_background_change.update()
        if self.act_ticker_change is not None:
            self.act_ticker_change.update()

    # Handle Events

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND:
                if event.unit % 15 == 0:
                    self.act_ticker_change = self.build_ticker_change_act()
                    self.act_ticker_change.start()
            if event.type == EVENT_EPOCH_MINUTE:
                self.act_background_change = self.build_background_change_act()
                self.act_background_change.start()

    # Acts

    def build_clock_show_act(self) -> Act:
        return Act(
            64,
            [
                (
                    0,
                    Animation(
                        self.clock_widget,
                        (self.width - 128, 0),
                        64,
                    ),
                ),
            ],
        )

    def build_weather_show_act(self) -> Act:
        return Act(
            64,
            [
                (
                    0,
                    Animation(
                        self.weather_widget,
                        (self.width - 192, 0),
                        64,
                    ),
                ),
            ],
        )

    def build_background_change_act(self) -> Act:
        return Act(
            128,
            [
                (
                    0,
                    Animation(
                        self.background_widget,
                        (0, 0 - self.height),
                        64,
                    ),
                ),
                (64, lambda: self.background_widget.set_random_image()),
                (
                    64,
                    Animation(
                        self.background_widget,
                        (0, 0),
                        64,
                        (0, 0 - self.height),
                    ),
                ),
            ],
        )

    def build_ticker_change_act(self) -> Act:
        return Act(
            176,
            [
                (
                    0,
                    Animation(
                        self.text_widget,
                        (4, self.height),
                        64,
                    ),
                ),
                (64, lambda: self.text_widget.set_random_content()),
                (
                    96,
                    Animation(self.text_widget, (4, 4), 64, (4, self.height)),
                ),
            ],
        )
