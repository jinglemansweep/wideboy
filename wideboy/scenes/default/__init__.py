import logging
from pygame import Clock, Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.hassentitytile import HassEntityTileSprite
from wideboy.sprites.homeassistant.entity_row import HomeAssistantEntityRowSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.rect import RectSprite
from wideboy.sprites.weather import WeatherAnimationSprite
from wideboy.sprites.image_helpers import MaterialIcons
from wideboy.scenes.base import BaseScene

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
            255,
            shuffle=True,
        )
        self.group.add(self.background_widget)

        # =====================================================================
        # WEATHER WIDGET
        # =====================================================================

        self.weather_widget = WeatherAnimationSprite(
            self,
            Rect(self.width - 128, -32, 128, 64),
            demo=settings.general.demo,
            size=Vector2(128, 128),
        )
        self.group.add(self.weather_widget)

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
        # NOTIFICATION WIDGET
        # =====================================================================

        self.notification_widget = NotificationSprite(
            self,
            Rect(32, 4, 768 - 320, 56),
            color_bg=Color(0, 0, 0, 192),
            color_fg=Color(255, 255, 255, 255),
        )
        self.group.add(self.notification_widget)

        # =====================================================================
        # HASS ENTITY ROW WIDGETS
        # =====================================================================

        hass_row_entities = [
            dict(
                entity_id="sensor.transmission_down_speed",
                icon=MaterialIcons.MDI_VPN_LOCK,
                icon_color=Color(255, 255, 255, 255),
                template="{{ states('sensor.transmission_down_speed') | int }}Mbps",
                cb_active=lambda state: float(state.state) > 0,
            ),
            dict(
                entity_id="sensor.ds920plus_volume_used",
                icon=MaterialIcons.MDI_DNS,
                icon_color=Color(255, 255, 0, 255),
                template="{{ states('sensor.ds920plus_volume_used') }}%",
            ),
            dict(
                entity_id="sensor.download_iperf_as42831_net",
                icon=MaterialIcons.MDI_DOWNLOAD,
                icon_color=Color(0, 255, 0, 255),
                template="{{ states('sensor.download_iperf_as42831_net') | int }}Mbps",
                cb_active=lambda state: float(state.state) < 750,
            ),
            dict(
                entity_id="sensor.upload_iperf_as42831_net",
                icon=MaterialIcons.MDI_UPLOAD,
                icon_color=Color(255, 0, 0, 255),
                template="{{ states('sensor.upload_iperf_as42831_net') | int }}Mbps",
                cb_active=lambda state: float(state.state) < 750,
            ),
            dict(
                entity_id="sensor.speedtest_ping",
                icon=MaterialIcons.MDI_WIFI,
                icon_color=Color(0, 0, 255, 255),
                template="{{ states('sensor.speedtest_ping') | int }}ms",
                cb_active=lambda state: float(state.state) > 10,
            ),
            dict(
                entity_id="sensor.black_bin",
                icon=MaterialIcons.MDI_DELETE,
                icon_color=Color(128, 128, 128, 255),
                template="{{ state_attr('sensor.black_bin', 'days') }}d",
                cb_active=lambda state: float(state.attributes["days"]) < 3,
            ),
            dict(
                entity_id="sensor.blue_bin",
                icon=MaterialIcons.MDI_DELETE,
                icon_color=Color(0, 128, 255, 255),
                template="{{ state_attr('sensor.blue_bin', 'days') }}d",
                cb_active=lambda state: float(state.attributes["days"]) < 3,
            ),
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
            ),
            dict(
                entity_id="switch.lounge_fans",
                icon=MaterialIcons.MDI_AC_UNIT,
                icon_color=Color(196, 196, 255, 255),
                template="ON",
                cb_active=lambda state: state.state == "on",
            ),
        ]

        self.hass_row = HomeAssistantEntityRowSprite(
            self,
            Rect(512, 48, 128, 16),
            hass_row_entities,
            color_bg=Color(0, 0, 0, 196),
        )
        self.group.add(self.hass_row)

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
