import logging
from pygame import Clock, Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_HOUR, EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.homeassistant.entity_row import HomeAssistantEntityRowSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.weather.animation import WeatherAnimationSprite
from wideboy.sprites.weather.temperature import WeatherTemperatureSprite
from wideboy.sprites.weather.wind import WeatherWindSprite
from wideboy.sprites.image_helpers import MaterialIcons
from wideboy.scenes.base import BaseScene

from wideboy.config import settings

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes.scene.default")


class NightScene(BaseScene):
    name = "night"

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
            settings.paths.images_backgrounds_night,
            255,
            shuffle=True,
        )
        self.group.add(self.background_widget)

        # =====================================================================
        # CLOCK WIDGET
        # =====================================================================

        CLOCK_POSITION = (self.width - 100, 0)
        CLOCK_COLOR_FG = Color(0, 0, 0, 192)
        CLOCK_COLOR_OUTLINE = Color(128, 255, 255, 255)

        self.clock_time_widget = TimeSprite(
            self,
            Rect(CLOCK_POSITION[0], CLOCK_POSITION[1], 96, 39),
            color_fg=CLOCK_COLOR_FG,
            color_outline=CLOCK_COLOR_OUTLINE,
            font_size=38,
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(CLOCK_POSITION[0], CLOCK_POSITION[1] + 39, 96, 16),
            color_fg=CLOCK_COLOR_FG,
            color_outline=CLOCK_COLOR_OUTLINE,
            font_size=14,
        )
        self.group.add(self.clock_date_widget)

        # =====================================================================
        # HASS ENTITY ROW WIDGETS
        # =====================================================================

        hass_row_entities = [
            dict(
                entity_id="binary_sensor.back_door_contact_sensor_contact",
                icon=MaterialIcons.MDI_DOOR,
                icon_color=Color(255, 64, 64, 255),
                template="Back",
                cb_active=lambda state: state.state == "on",
            ),
            dict(
                entity_id="binary_sensor.front_door_contact_sensor_contact",
                icon=MaterialIcons.MDI_DOOR,
                icon_color=Color(255, 64, 64, 255),
                template="Front",
                cb_active=lambda state: state.state == "on",
            )
        ]

        self.hass_row = HomeAssistantEntityRowSprite(
            self,
            Rect(512, 48, 128, 16),
            hass_row_entities,
            color_bg=Color(0, 0, 0, 196),
        )
        self.group.add(self.hass_row)

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
        self.hass_row.rect.topright = self.width - 128, 0

    # Handle Events

    def handle_events(self, events: list[Event]) -> None:
        super().handle_events(events)
        for event in events:
            if event.type == EVENT_EPOCH_HOUR:
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
