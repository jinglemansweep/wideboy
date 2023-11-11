import logging
from pygame import Clock, Color, Event, Rect, Vector2, JOYBUTTONUP
from typing import TYPE_CHECKING
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_ACTION_A, GAMEPAD
from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.background import BackgroundSprite
from wideboy.sprites.calendar import CalendarSprite
from wideboy.sprites.clock import DateSprite, TimeSprite
from wideboy.sprites.homeassistant.entity_row import (
    HomeAssistantEntityRowSprite,
    HomeAssistantEntityTile,
)
from wideboy.sprites.homeassistant.entity_grid import HomeAssistantEntityGridSprite
from wideboy.sprites.notification import NotificationSprite
from wideboy.sprites.weather.animation import WeatherAnimationSprite
from wideboy.sprites.weather.temperature import WeatherTemperatureSprite
from wideboy.sprites.weather.wind import WeatherWindSprite
from wideboy.sprites.image_helpers import MaterialIcons
from wideboy.scenes.base import BaseScene
from wideboy.scenes.default.tiles import (
    GridTileStepsLouis,
    GridTileVPN,
    GridTileTransmission,
    GridTileDS920Plus,
    GridTileSpeedtestDownload,
    GridTileSpeedtestUpload,
    GridTileSpeedtestPing,
    GridTileBackDoor,
    GridTileFrontDoor,
    GridTileHouseManual,
    GridTileSwitchLoungeFans,
    GridTileElectricityCurrentDemand,
    GridTileElectricityCurrentRate,
    GridTileElectricityHourlyRate,
    GridTileElectricityCurrentAccumulativeCost,
    GridTileBatteryLevel,
    GridTileBatteryDischargeRemainingTime,
    GridTileBatteryChargeRemainingTime,
    GridTileBatteryAcInPower,
    GridTileBatteryAcOutPower,
)

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

        GRID_ENTITY_WIDTH = 50
        GRID_ENTITY_START_X = self.width - 384
        GRID_ENTITY_MARGIN_X = 1

        grid_entity_cx = GRID_ENTITY_START_X

        hass_grid_home_entities = [
            GridTileBackDoor(),
            GridTileFrontDoor(),
            GridTileHouseManual(),
            GridTileSwitchLoungeFans(),
        ]

        self.hass_grid_home = HomeAssistantEntityGridSprite(
            self,
            Rect(grid_entity_cx, 0, GRID_ENTITY_WIDTH, 64),
            cell_size=(GRID_ENTITY_WIDTH, 12),
            padding=(0, 0),
            title="Home",
            cells=hass_grid_home_entities,
            accent_color=Color(255, 0, 255, 255),
        )
        self.group.add(self.hass_grid_home)

        grid_entity_cx += GRID_ENTITY_WIDTH + GRID_ENTITY_MARGIN_X

        hass_grid_main_entities = [
            GridTileDS920Plus(),
        ]

        self.hass_grid_main = HomeAssistantEntityGridSprite(
            self,
            Rect(grid_entity_cx, 0, GRID_ENTITY_WIDTH, 64),
            cell_size=(GRID_ENTITY_WIDTH, 12),
            padding=(0, 0),
            title="Main",
            cells=hass_grid_main_entities,
            accent_color=Color(255, 0, 0, 255),
        )
        self.group.add(self.hass_grid_main)

        grid_entity_cx += GRID_ENTITY_WIDTH + GRID_ENTITY_MARGIN_X

        hass_grid_network_entities = [
            GridTileVPN(),
            # GridTileTransmission(),
            GridTileSpeedtestDownload(),
            GridTileSpeedtestUpload(),
            GridTileSpeedtestPing(),
        ]

        self.hass_grid_network = HomeAssistantEntityGridSprite(
            self,
            Rect(grid_entity_cx, 0, GRID_ENTITY_WIDTH, 64),
            cell_size=(GRID_ENTITY_WIDTH, 12),
            padding=(0, 0),
            title="Network",
            cells=hass_grid_network_entities,
            accent_color=Color(255, 255, 0, 255),
        )
        self.group.add(self.hass_grid_network)

        grid_entity_cx += GRID_ENTITY_WIDTH + GRID_ENTITY_MARGIN_X

        hass_grid_battery_entities = [
            GridTileBatteryLevel(),
            GridTileBatteryDischargeRemainingTime(),
            GridTileBatteryChargeRemainingTime(),
            GridTileBatteryAcInPower(),
            GridTileBatteryAcOutPower(),
        ]

        self.hass_grid_battery = HomeAssistantEntityGridSprite(
            self,
            Rect(grid_entity_cx, 0, GRID_ENTITY_WIDTH, 64),
            cell_size=(GRID_ENTITY_WIDTH, 12),
            padding=(0, 0),
            title="Battery",
            cells=hass_grid_battery_entities,
            accent_color=Color(0, 0, 255, 255),
        )
        self.group.add(self.hass_grid_battery)

        grid_entity_cx += GRID_ENTITY_WIDTH + GRID_ENTITY_MARGIN_X

        hass_grid_electricity_entities = [
            GridTileElectricityCurrentDemand(),
            GridTileElectricityCurrentRate(),
            GridTileElectricityHourlyRate(),
            GridTileElectricityCurrentAccumulativeCost(),
        ]

        self.hass_grid_electricity = HomeAssistantEntityGridSprite(
            self,
            Rect(grid_entity_cx, 0, GRID_ENTITY_WIDTH, 64),
            cell_size=(GRID_ENTITY_WIDTH, 12),
            padding=(0, 0),
            title="Power",
            cells=hass_grid_electricity_entities,
            accent_color=Color(0, 255, 0, 255),
        )
        self.group.add(self.hass_grid_electricity)

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
