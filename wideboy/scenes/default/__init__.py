import asyncio
import logging
from pygame import Clock, Color, Event, Rect, Surface, Vector2, JOYBUTTONUP

from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import ClockSprite
from wideboy.sprites.hassentitytile import HassEntityTileSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.rect import RectSprite
from wideboy.sprites.qrcode import QRCodeSprite
from wideboy.sprites.text import TextSprite
from wideboy.sprites.weather import WeatherSprite
from wideboy.scenes.base import BaseScene

from wideboy.config import settings


logger = logging.getLogger("scenes.scene.default")


class DefaultScene(BaseScene):
    name = "default"

    def __init__(
        self,
        surface: Surface,
        bg_color: Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(surface, bg_color)

    def setup(self):
        super().setup()
        # Setup background widget
        self.background_widget = BackgroundSprite(
            Rect(
                0,
                0 - self.height,
                self.width,
                self.height,
            ),
            (self.width, self.height),
            255,
            shuffle=True,
        )
        self.group.add(self.background_widget)
        # Setup faded foreground layer widget
        self.layer_faded = RectSprite(
            Rect(self.width - 256, 0, 256, 64),
            color_bg=Color(0, 0, 0, 255 - 64),
        )
        self.group.add(self.layer_faded)
        # Setup calendar widget
        self.calendar_widget = CalendarSprite(
            Rect(self.width - 128, 49, 128, 24), "calendar.wideboy", font_size=10
        )
        self.group.add(self.calendar_widget)
        # Setup clock widget
        self.clock_widget = ClockSprite(
            Rect(
                self.width - 128,
                0,
                128,
                48,
            ),
        )
        self.group.add(self.clock_widget)
        # Setup weather widget
        self.weather_widget = WeatherSprite(
            Rect(576, 0, 64, 64), color_temp=Color(255, 255, 255, 64), debug=False
        )
        self.group.add(self.weather_widget)
        # Setup notification widget
        self.notification_widget = NotificationSprite(
            Rect(32, 4, 768 - 320, 56),
            color_bg=Color(0, 0, 0, 192),
            color_fg=Color(255, 255, 255, 255),
        )
        self.group.add(self.notification_widget)
        # HASS Entity Tile Widgets
        bin_rect = Rect(self.width - 18, 0, 16, 16)
        self.hass_bin_black = HassEntityTileSprite(
            bin_rect,
            "sensor.black_bin",
            HassEntityTileSprite.MDI_DELETE,
            lambda entity: entity.state.attributes["days"] < 2,
            Color(128, 128, 128, 255),
            font_size=16,
        )
        self.group.add(self.hass_bin_black)
        self.hass_bin_blue = HassEntityTileSprite(
            bin_rect,
            "sensor.blue_bin",
            HassEntityTileSprite.MDI_DELETE,
            lambda entity: entity.state.attributes["days"] < 2,
            Color(0, 128, 255, 255),
            font_size=16,
        )
        self.group.add(self.hass_bin_blue)
        # Run initial acts
        self.act_clock_show = self.build_clock_show_act()
        self.act_clock_show.start()
        self.act_background_change = self.build_background_change_act()
        self.act_background_change.start()

    def update(
        self,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(clock, delta, events)
        if self.act_clock_show is not None:
            self.act_clock_show.update()
        if self.act_background_change is not None:
            self.act_background_change.update()

    # Handle Events

    def handle_events(self, events: list[Event]) -> None:
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                if event.unit % 5 == 0:
                    self.background_widget.glob_images()
                if event.unit % settings.backgrounds.change_interval_mins == 0:
                    self.run_background_change_act()
            if event.type == EVENT_ACTION_A or (
                event.type == JOYBUTTONUP and event.button == GAMEPAD["BUTTON_A"]
            ):
                self.run_background_change_act()

    def run_background_change_act(self) -> None:
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
                        Vector2(self.width - 128, 0),
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
                        Vector2(0, 0 - self.height),
                        64,
                    ),
                ),
                (64, lambda: self.background_widget.render_next_image()),
                (
                    64,
                    Animation(
                        self.background_widget,
                        Vector2(0, 0),
                        64,
                        Vector2(0, 0 - self.height),
                    ),
                ),
            ],
        )
