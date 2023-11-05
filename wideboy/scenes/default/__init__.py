import logging
from pygame import Clock, Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
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
        # HASS ENTITY ROW WIDGETS
        # =====================================================================

        hass_row_main_entities = [
            dict(
                icon=MaterialIcons.MDI_DIRECTIONS_WALK,
                icon_color=Color(255, 0, 255, 255),
                template="{state[sensor.steps_louis]}",
                watch_entities=["sensor.steps_louis"],
            ),
            # active when public IP is home IP
            dict(
                icon=MaterialIcons.MDI_LOCK,
                icon_color=Color(255, 0, 0, 255),
                template="VPN DOWN ({state[sensor.privacy_ip_info]})",
                cb_active=lambda state: state["sensor.privacy_ip_info"]
                == settings.secrets.home_ip,
                watch_entities=["sensor.privacy_ip_info"],
            ),
            dict(
                icon=MaterialIcons.MDI_VPN_LOCK,
                icon_color=Color(255, 255, 255, 255),
                template="{state[sensor.transmission_down_speed]:.0f}Mbps",
                cb_active=lambda state: state["sensor.transmission_down_speed"] > 0,
                watch_entities=["sensor.transmission_down_speed"],
            ),
            dict(
                icon=MaterialIcons.MDI_DNS,
                icon_color=Color(255, 255, 0, 255),
                template="{state[sensor.ds920plus_volume_used]:.0f}%",
                cb_active=lambda state: state["sensor.ds920plus_volume_used"] > 66.66,
                watch_entities=["sensor.ds920plus_volume_used"],
            ),
            dict(
                icon=MaterialIcons.MDI_DOWNLOAD,
                icon_color=Color(0, 255, 0, 255),
                template="{state[sensor.speedtest_download_average]:.0f}Mbps",
                cb_active=lambda state: state["sensor.speedtest_download_average"]
                < 600,
                watch_entities=["sensor.speedtest_download_average"],
            ),
            dict(
                icon=MaterialIcons.MDI_UPLOAD,
                icon_color=Color(255, 0, 0, 255),
                template="{state[sensor.speedtest_upload_average]:.0f}Mbps",
                cb_active=lambda state: state["sensor.speedtest_upload_average"] < 600,
                watch_entities=["sensor.speedtest_upload_average"],
            ),
            dict(
                icon=MaterialIcons.MDI_WIFI,
                icon_color=Color(0, 0, 255, 255),
                template="{state[sensor.speedtest_ping_average]:.0f}ms",
                cb_active=lambda state: state["sensor.speedtest_ping_average"] > 10,
                watch_entities=["sensor.speedtest_ping_average"],
            ),
            # dict(
            #    icon=MaterialIcons.MDI_DELETE,
            #    icon_color=Color(192, 192, 192, 255),
            #    template="{{ state_attr('calendar.bin_collection', 'message') }}",
            #    cb_active=lambda state: float(state.state) <= 1,
            #    watch_entities=["sensor.bin_collection_days"],
            # ),
            dict(
                icon=MaterialIcons.MDI_DOOR,
                icon_color=Color(255, 64, 64, 255),
                template="Back",
                cb_active=lambda state: state[
                    "binary_sensor.back_door_contact_sensor_contact"
                ]
                == "on",
                watch_entities=["binary_sensor.back_door_contact_sensor_contact"],
            ),
            dict(
                icon=MaterialIcons.MDI_DOOR,
                icon_color=Color(255, 64, 64, 255),
                template="Front",
                cb_active=lambda state: state[
                    "binary_sensor.front_door_contact_sensor_contact"
                ]
                == "on",
                watch_entities=["binary_sensor.front_door_contact_sensor_contact"],
            ),
            dict(
                icon=MaterialIcons.MDI_TOGGLE_ON,
                icon_color=Color(255, 0, 0, 255),
                template="MANUAL",
                cb_active=lambda state: state["input_boolean.house_manual"] == "on",
                watch_entities=["input_boolean.house_manual"],
            ),
            dict(
                icon=MaterialIcons.MDI_AC_UNIT,
                icon_color=Color(196, 196, 255, 255),
                template="ON",
                cb_active=lambda state: state["switch.lounge_fans"] == "on",
                watch_entities=["switch.lounge_fans"],
            ),
        ]

        self.hass_row_main = HomeAssistantEntityRowSprite(
            self,
            Rect(512, 48, 128, 16),
            hass_row_main_entities,
            color_bg=Color(0, 0, 0, 196),
        )
        self.group.add(self.hass_row_main)

        hass_row_power_entities = [
            dict(
                icon=MaterialIcons.MDI_BOLT,
                icon_color=Color(192, 192, 192, 255),
                template="{state[sensor.octopus_energy_electricity_current_demand]:.0f}w",
                watch_entities=["sensor.octopus_energy_electricity_current_demand"],
            ),
            dict(
                icon=MaterialIcons.MDI_SYMBOL_AT,
                icon_color=Color(192, 192, 192, 255),
                template="£{state[sensor.octopus_energy_electricity_current_rate]:.2f}",
                watch_entities=["sensor.octopus_energy_electricity_current_rate"],
            ),
            dict(
                icon=MaterialIcons.MDI_CURRENCY_DOLLAR,
                icon_color=Color(255, 64, 64, 255),
                template="£{state[sensor.electricity_hourly_rate]:.2f}",
                watch_entities=[
                    "sensor.electricity_hourly_rate",
                ],
            ),
            dict(
                icon=MaterialIcons.MDI_SCHEDULE,
                icon_color=Color(255, 64, 64, 255),
                template="£{state[sensor.octopus_energy_electricity_current_accumulative_cost]:.2f}",
                watch_entities=[
                    "sensor.octopus_energy_electricity_current_accumulative_cost"
                ],
            ),
        ]

        self.hass_row_power = HomeAssistantEntityRowSprite(
            self,
            Rect(512, 48, 128, 16),
            hass_row_power_entities,
            color_bg=Color(0, 0, 0, 196),
        )
        self.group.add(self.hass_row_power)

        hass_row_battery_entities = [
            dict(
                icon=MaterialIcons.MDI_BATTERY,
                icon_color=Color(192, 192, 192, 255),
                template="{state[sensor.delta_2_max_downstairs_battery_level]:.0f}%",
                watch_entities=["sensor.delta_2_max_downstairs_battery_level"],
            ),
            dict(
                icon=MaterialIcons.MDI_LOOP,
                icon_color=Color(192, 192, 192, 255),
                template="{state[sensor.delta_2_max_downstairs_cycles]:.0f}",
                watch_entities=["sensor.delta_2_max_downstairs_cycles"],
            ),
            dict(
                icon=MaterialIcons.MDI_HOURGLASS,
                icon_color=Color(255, 64, 64, 255),
                template=lambda state: f"{int(state['sensor.delta_2_max_downstairs_discharge_remaining_time']//60)}h{int(state['sensor.delta_2_max_downstairs_discharge_remaining_time']%60)}m",
                cb_active=lambda state: state[
                    "sensor.delta_2_max_downstairs_discharge_remaining_time"
                ]
                or 0 > 0,
                watch_entities=[
                    "sensor.delta_2_max_downstairs_discharge_remaining_time"
                ],
            ),
            dict(
                icon=MaterialIcons.MDI_HOURGLASS,
                icon_color=Color(64, 255, 64, 255),
                template=lambda state: f"{int(state['sensor.delta_2_max_downstairs_charge_remaining_time']//60)}h{int(state['sensor.delta_2_max_downstairs_charge_remaining_time']%60)}m",
                cb_active=lambda state: state[
                    "sensor.delta_2_max_downstairs_charge_remaining_time"
                ]
                or 0 > 0,
                watch_entities=["sensor.delta_2_max_downstairs_charge_remaining_time"],
            ),
            dict(
                icon=MaterialIcons.MDI_POWER,
                icon_color=Color(255, 64, 64, 255),
                template="{state[sensor.delta_2_max_downstairs_ac_in_power]:.0f}w",
                cb_active=lambda state: state[
                    "sensor.delta_2_max_downstairs_ac_in_power"
                ]
                or 0 > 0,
                watch_entities=["sensor.delta_2_max_downstairs_ac_in_power"],
            ),
        ]

        self.hass_row_battery = HomeAssistantEntityRowSprite(
            self,
            Rect(512, 48, 128, 16),
            hass_row_battery_entities,
            color_bg=Color(0, 0, 0, 196),
        )
        self.group.add(self.hass_row_battery)

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
        self.hass_row_main.rect.topright = self.width - 128 - 3, 2
        self.hass_row_power.rect.topright = self.width - 128 - 3, 17
        self.hass_row_battery.rect.topright = self.width - 128 - 3, 32

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
