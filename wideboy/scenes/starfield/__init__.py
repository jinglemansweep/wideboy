import logging
import random
from pygame import Clock, Color, Event, Rect, Vector2
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_SECOND, EVENT_ACTION_A
from wideboy.sprites.clock import DateSprite, TimeSprite

# from wideboy.sprites.rotogrid import RotoGridSprite
# from wideboy.sprites.sphere import SphereSprite
from wideboy.sprites.starfield import StarfieldSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.scenes.animation import Act, Animation
from wideboy.scenes.base import BaseScene

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes.scene.night")


class StarfieldScene(BaseScene):
    name = "starfield"

    def __init__(
        self,
        engine: "Engine",
        bg_color: Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(engine, bg_color)

    def setup(self):
        super().setup()

        # =====================================================================
        # STARFIELD WIDGET
        # =====================================================================

        self.starfield_widget = StarfieldSprite(
            self,
            Rect(0, 0, self.width, self.height),
            color_fg=Color(255, 255, 255, 192),
        )
        self.group.add(self.starfield_widget)

        # =====================================================================
        # SPHERE WIDGET
        # =====================================================================

        """
        self.sphere_widget = SphereSprite(
            self,
            Rect(576, -32, 768 - 576, 128),
            color_fg=Color(0, 0, 255, 64),
            radius=100,
        )
        self.group.add(self.sphere_widget)
        """

        # =====================================================================
        # CLOCK WIDGET
        # =====================================================================

        self.clock_time_pos: tuple[int, int] = (self.width - 128, -7)
        self.clock_date_offset: tuple[int, int] = [0, 48]
        self.clock_time_widget = TimeSprite(
            self,
            Rect(self.clock_time_pos[0], self.clock_time_pos[1], 128, 48),
            font_size=48,
            color_fg=Color(0, 0, 0, 255),
            color_outline=Color(255, 0, 255, 64),
            rainbow="outline",
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(
                self.clock_time_pos[0] + self.clock_date_offset[0],
                self.clock_time_pos[1] + self.clock_date_offset[1],
                128,
                24,
            ),
            color_fg=Color(0, 0, 0, 255),
            color_outline=Color(128, 0, 128, 255),
            rainbow="outline",
        )
        self.group.add(self.clock_date_widget)

        # =====================================================================
        # NOTIFICATION WIDGET
        # =====================================================================

        self.notification_widget = NotificationSprite(
            self,
            Rect(0, 0, 768, 64),
            color_bg=Color(0, 0, 0, 128),
            color_fg=Color(128, 128, 255, 255),
            color_progress=Color(0, 0, 255, 255),
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
            if event.type == EVENT_ACTION_A or (
                event.type == EVENT_EPOCH_SECOND and event.unit % 30 == 0
            ):
                self.animate_clock()

    def animate_clock(self):
        x = random.randint(
            0,
            (
                self.width
                - max(
                    self.clock_time_widget.rect.width, self.clock_date_widget.rect.width
                )
            ),
        )
        y = random.randint(-11, -3)
        self.animation_group.add(
            Act(
                64,
                [
                    (0, Animation(self.clock_time_widget, Vector2(x, y), 64)),
                    (
                        0,
                        Animation(
                            self.clock_date_widget,
                            Vector2(
                                x + self.clock_date_offset[0],
                                y + self.clock_date_offset[1],
                            ),
                            64,
                        ),
                    ),
                ],
            )
        )