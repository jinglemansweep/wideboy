import logging
from pygame import Clock, Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.tile_grid import TileGrid
from wideboy.sprites.weather.animation import WeatherAnimationSprite
from wideboy.sprites.weather.temperature import WeatherTemperatureSprite
from wideboy.sprites.weather.wind import WeatherWindSprite
from wideboy.scenes.base import BaseScene
from wideboy.scenes.default.tiles import CELLS


from wideboy.config import settings

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes.scene.default")


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
                640,
                self.height,
            ),
            settings.paths.images_backgrounds,
            255,
            shuffle=True,
        )
        self.group.add(self.background_widget)

        # =====================================================================
        # WEATHER WIDGETS
        # =====================================================================

        self.weather_animation_widget = WeatherAnimationSprite(
            self,
            Rect(self.width - 128, -32, 128, 64),
            demo=settings.general.demo,
            size=Vector2(128, 128),
        )
        self.group.add(self.weather_animation_widget)

        self.weather_temp_widget = WeatherTemperatureSprite(
            self,
            Rect(self.width - 128 + 4, 0, 32, 28),
        )
        self.group.add(self.weather_temp_widget)

        self.weather_wind_widget = WeatherWindSprite(
            self,
            Rect(self.width - 128 + 6, 22, 32, 32),
        )
        self.group.add(self.weather_wind_widget)

        # =====================================================================
        # CLOCK WIDGET
        # =====================================================================

        self.clock_time_widget = TimeSprite(
            self,
            Rect(self.width - 96, -7, 96, 39),
            color_fg=Color(255, 255, 0, 255),
            font_size=38,
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(self.width - 96, 29, 96, 16),
            color_fg=Color(255, 255, 255, 255),
            font_size=14,
        )
        self.group.add(self.clock_date_widget)

        # =====================================================================
        # CALENDAR WIDGET
        # =====================================================================

        self.calendar_widget = CalendarSprite(
            self,
            Rect(self.width - 96, 51, 96, 15),
            "calendar.wideboy",
            font_size=9,
            color_fg=Color(255, 128, 255, 255),
        )
        self.group.add(self.calendar_widget)

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

        # =====================================================================
        # SCENE STARTUP
        # =====================================================================

        self.act_background_change = self.build_background_change_act()
        self.act_background_change.start()

    # Update

    def update(
        self,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(clock, delta, events)
        self.tile_grid.rect.topright = (self.width - 130, 0)

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
                    self.run_background_change_act()
            if event.type == EVENT_ACTION_A or (
                event.type == JOYBUTTONUP and event.button == GAMEPAD["BUTTON_A"]
            ):
                self.run_background_change_act()

    def run_background_change_act(self) -> None:
        self.animation_group.add(self.build_background_change_act())

    # Acts

    def build_background_change_act(self) -> Act:
        return Act(
            64,
            [
                (
                    0,
                    Animation(
                        self.background_widget,
                        Vector2(0, 0 - self.height),
                        32,
                    ),
                ),
                (32, lambda: self.background_widget.render_next_image()),
                (
                    32,
                    Animation(
                        self.background_widget,
                        Vector2(0, 0),
                        32,
                        Vector2(0, 0 - self.height),
                    ),
                ),
            ],
        )
