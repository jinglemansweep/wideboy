import logging
from pygame import Clock, Color, Event, Rect, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.rect import RectSprite
from wideboy.sprites.tile_grid import TileGrid
from wideboy.scenes.base import BaseScene
from wideboy.scenes.default.tiles import CELLS


from wideboy.config import settings

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes.scene.default")

CLOCK_WIDTH = 90


class DefaultScene(BaseScene):
    name = "default"

    def __init__(
        self,
        engine: "Engine",
        bg_color: Color = Color(0, 0, 0, 255),
    ) -> None:
        super().__init__(engine, bg_color)

    def setup(self):
        super().setup()

        # =====================================================================
        # ARTYFARTY BACKGROUND WIDGET
        # =====================================================================

        self.background_widget = BackgroundSprite(
            self,
            Rect(
                0,
                0,
                self.width,
                self.height,
            ),
            settings.paths.images_backgrounds,
            shuffle=True,
        )
        self.group.add(self.background_widget)

        # =====================================================================
        # CLOCK WIDGET
        # =====================================================================

        self.clock_background = RectSprite(
            self,
            Rect(self.width - CLOCK_WIDTH, 0, CLOCK_WIDTH, 40),
            Color(0, 0, 0, 192),
        )
        self.group.add(self.clock_background)

        self.clock_time_widget = TimeSprite(
            self,
            Rect(self.width - CLOCK_WIDTH, 1, CLOCK_WIDTH, 30),
            color_fg=Color(255, 255, 0, 255),
            font_size=30,
            pos_adj=(1, 0),
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(self.width - CLOCK_WIDTH, 25, CLOCK_WIDTH, 16),
            color_fg=Color(255, 255, 255, 255),
            font_size=14,
            uppercase=False,
        )
        self.group.add(self.clock_date_widget)

        # =====================================================================
        # TILE GRID WIDGET
        # =====================================================================

        self.tile_grid = TileGrid(self, CELLS)
        self.group.add(self.tile_grid)

        # =====================================================================
        # NOTIFICATION WIDGET
        # =====================================================================

        self.notification_widget = NotificationSprite(
            self,
            Rect(0, 0, 640, 64),
            color_bg=Color(0, 0, 0, 192),
            color_fg=Color(255, 255, 255, 255),
            font_size=30,
            font_padding=12,
        )
        self.group.add(self.notification_widget)

    # Update

    def update(
        self,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(clock, delta, events)
        self.tile_grid.rect.topright = (self.width - CLOCK_WIDTH, 0)

    # Handle Events

    def handle_events(self, events: list[Event]) -> None:
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                if event.unit % 5 == 0:
                    self.background_widget.glob_images(
                        settings.paths.images_backgrounds
                    )
                if event.unit % settings.backgrounds.change_interval_mins == 0:
                    self.background_widget.change_image()
            if event.type == EVENT_ACTION_A or (
                event.type == JOYBUTTONUP and event.button == GAMEPAD["BUTTON_A"]
            ):
                self.background_widget.change_image()
