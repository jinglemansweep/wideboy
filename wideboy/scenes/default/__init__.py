import logging
from pygame import Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.hassentitytile import HassEntityTileSprite
from wideboy.sprites.homeassistant import HomeAssistantTemplateSprite
from wideboy.sprites.material_icon import MaterialIconSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.rect import RectSprite
from wideboy.sprites.weather import WeatherSprite
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

        # Setup background widget
        self.background_widget = BackgroundSprite(
            self,
            Rect(
                0,
                0,
                self.width,
                self.height,
            ),
            (self.width, self.height),
            255,
            shuffle=True,
        )
        self.group.add(self.background_widget)

        # Setup weather widget
        self.weather_widget = WeatherSprite(
            self,
            Rect(self.width - 128, 0, 128, 64),
            color_temp=Color(255, 255, 255, 64),
            demo=settings.general.demo,
        )
        self.group.add(self.weather_widget)

        # Setup calendar widget
        self.calendar_widget = CalendarSprite(
            self, Rect(self.width - 96, 49, 96, 24), "calendar.wideboy"
        )
        self.group.add(self.calendar_widget)

        # Setup clock widgets
        clock_pos_adj: tuple[int, int] = (0, 0)
        self.clock_time_widget = TimeSprite(
            self,
            Rect(self.width - 96, -6, 96, 32),
            color_fg=Color(255, 255, 255, 128),
            font_size=28,
            align="right",
        )
        self.group.add(self.clock_time_widget)
        self.clock_date_widget = DateSprite(
            self,
            Rect(self.width - 96, 20, 96, 24),
            color_fg=Color(255, 255, 0, 128),
            font_size=14,
            align="right",
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

        # Setup bin collection widgets
        bin_rect = Rect(self.width - 183, 40, 32, 32)
        self.hass_bin_black = HassEntityTileSprite(
            self,
            bin_rect,
            MaterialIcons.MDI_DELETE,
            entity_id="sensor.black_bin",
            state_callback=lambda state: state.attributes["days"] < 2,
        )
        self.group.add(self.hass_bin_black)
        self.hass_bin_blue = HassEntityTileSprite(
            self,
            bin_rect,
            MaterialIcons.MDI_DELETE,
            entity_id="sensor.blue_bin",
            state_callback=lambda state: state.attributes["days"] < 2,
            color_icon=Color(0, 128, 255, 255),
        )
        self.group.add(self.hass_bin_blue)

        # Speedtest Widgets
        self.icon_speedtest = MaterialIconSprite(
            self,
            Rect(self.width - 256, 0, 16, 16),
            MaterialIcons.MDI_SYNC_ALT,
            16,
            color_fg=Color(0, 255, 0, 255),
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.icon_speedtest)
        self.template_speedtest = HomeAssistantTemplateSprite(
            self,
            Rect(self.width - 256 + 18, 2, 96, 16),
            "{{ states('sensor.download_iperf_as42831_net') | int }}|{{ states('sensor.upload_iperf_as42831_net') | int }}|{{ states('sensor.speedtest_ping') | int }}ms",
            font_size=9,
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.template_speedtest)

        # Transmission Widgets
        self.icon_transmission = MaterialIconSprite(
            self,
            Rect(self.width - 256, 14, 16, 16),
            MaterialIcons.MDI_VPN_LOCK,
            16,
            color_fg=Color(0, 255, 255, 255),
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.icon_transmission)
        self.template_transmission = HomeAssistantTemplateSprite(
            self,
            Rect(self.width - 256 + 18, 17, 96, 16),
            "{{ states('sensor.transmission_active_torrents') | int }}/{{ states('sensor.transmission_total_torrents') | int }} | {{ states('sensor.transmission_down_speed') | float | round(1) }}Mbs",
            font_size=9,
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.template_transmission)

        # NAS Widgets
        self.icon_nas_disk = MaterialIconSprite(
            self,
            Rect(self.width - 256, 30, 16, 16),
            MaterialIcons.MDI_DNS,
            16,
            color_fg=Color(255, 255, 0, 255),
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.icon_nas_disk)
        self.template_nas_volume_used = HomeAssistantTemplateSprite(
            self,
            Rect(self.width - 256 + 18, 32, 96, 16),
            "{{ states('sensor.ds920plus_volume_used') | float | round(2) }}%",
            font_size=9,
            color_outline=Color(0, 0, 0, 255),
        )
        self.group.add(self.template_nas_volume_used)

        # Run initial acts
        self.act_background_change = self.build_background_change_act()
        self.act_background_change.start()

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
