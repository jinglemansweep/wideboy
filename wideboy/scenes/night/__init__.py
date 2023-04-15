import logging
from pygame import Clock, Color, Event, Rect, Surface
from wideboy.sprites.clock import ClockSprite
from wideboy.sprites.starfield import StarfieldSprite
from wideboy.sprites.notification import NotificationSprite

from wideboy.scenes.base import BaseScene

from wideboy.config import settings


logger = logging.getLogger("scenes.scene.night")


class NightScene(BaseScene):
    name = "night"

    def __init__(
        self,
        surface: Surface,
        bg_color: Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(surface, bg_color)

    def setup(self):
        super().setup()

        # Starfield widget
        self.starfield_widget = StarfieldSprite(Rect(0, 0, self.width, self.height))
        self.group.add(self.starfield_widget)

        # Setup clock widget
        self.clock_widget = ClockSprite(
            Rect(self.width - 96, 0, 96, 48),
        )
        self.group.add(self.clock_widget)

        # Setup notification widget
        self.notification_widget = NotificationSprite(
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
