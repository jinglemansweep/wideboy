import logging
from pygame import Clock, Color, Event, Rect, Surface
from typing import TYPE_CHECKING
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.starfield import StarfieldSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.scenes.base import BaseScene

from wideboy.config import settings

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes.scene.night")


class NightScene(BaseScene):
    name = "night"

    def __init__(
        self,
        engine: "Engine",
        bg_color: Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(engine, bg_color)

    def setup(self):
        super().setup()

        # Starfield widget
        self.starfield_widget = StarfieldSprite(
            self,
            Rect(0, 0, self.width, self.height),
            color_fg=Color(255, 255, 255, 192),
        )
        self.group.add(self.starfield_widget)

        # Setup clock widget
        clock_pos_adj: tuple[int, int] = (0, 0)
        self.clock_time_widget = TimeSprite(
            self,
            Rect(self.width - 128 + clock_pos_adj[0], -7 + clock_pos_adj[1], 128, 48),
            font_size=48,
            color_fg=Color(0, 0, 0, 0),
            color_outline=Color(255, 0, 255, 64),
            rainbow="outline",
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(self.width - 128 + clock_pos_adj[0], 41 + clock_pos_adj[1], 128, 24),
            color_fg=Color(0, 0, 0, 0),
            color_outline=Color(128, 0, 128, 255),
            rainbow="outline",
        )
        self.group.add(self.clock_date_widget)

        # Setup notification widget
        self.notification_widget = NotificationSprite(
            self,
            Rect(32, 4, 768 - 320, 56),
            color_bg=Color(0, 0, 0, 192),
            color_fg=Color(255, 255, 255, 255),
        )
        self.group.add(self.notification_widget)

    def update(
        self,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(clock, delta, events)

    # Handle Events

    def handle_events(self, events: list[Event]) -> None:
        super().handle_events(events)
        for event in events:
            pass
