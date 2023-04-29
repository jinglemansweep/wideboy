import logging
import os
import pygame
import random
from pygame import Clock, Color, Event, Rect, Surface, Vector2, SRCALPHA
from typing import Optional, Dict, List

# from wideboy.mqtt.homeassistant import HASS
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    render_arrow,
    load_image,
    scale_surface,
)
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_EPOCH_SECOND
from wideboy.sprites.weather.resources import IMAGE_MAPPING

from wideboy.config import settings

logger = logging.getLogger("sprite.weather")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        color_bg: Color = Color(0, 0, 0, 0),
        color_temp: Color = Color(255, 255, 255, 255),
        color_rain_prob: Color = Color(255, 255, 0, 255),
        color_wind: Color = Color(255, 255, 255, 255),
        update_interval_mins: int = 15,
        demo: bool = False,
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_temp = color_temp
        self.color_rain_prob = color_rain_prob
        self.color_wind = color_wind
        self.update_interval_mins = update_interval_mins
        self.demo = demo
        self.icon_summary = None
        self.entity_weather_code = "sensor.openweathermap_weather_code"
        self.entity_condition = "sensor.openweathermap_condition"
        self.entity_wind_speed = "sensor.openweathermap_wind_speed"
        self.entity_wind_bearing = "sensor.openweathermap_wind_bearing"
        self.entity_temp = "sensor.openweathermap_temperature"
        self.entity_forecast_precipitation = (
            "sensor.openweathermap_forecast_precipitation_probability"
        )
        self.image_path = os.path.join(
            settings.paths.images_weather,
            "premium",
        )
        self.image_cache: dict[str, List[Surface]] = dict()
        self.image_frame = 0
        self.weather: Optional[Dict] = None
        self.update_state()
        self.render_text_surfaces()
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if (
                event.type == EVENT_EPOCH_MINUTE
                and event.unit % self.update_interval_mins == 0
            ) or self.weather is None:
                self.update_state()
                self.render_text_surfaces()
            if self.demo and event.type == EVENT_EPOCH_SECOND and event.unit % 10 == 0:
                self.weather["weather_code"] = random.choice(list(IMAGE_MAPPING.keys()))
        self.render()

    def render_text_surfaces(self) -> None:
        self.surface_temp = self._render_temperature()
        self.surface_rain_prob = self._render_precipitation()
        self.surface_wind = self._render_wind()

    def update_state(self) -> None:
        try:
            sun = self.scene.engine.hass.client.get_entity(entity_id="sun.sun")
            weather_code = self.scene.engine.hass.client.get_entity(
                entity_id=self.entity_weather_code
            )
            wind_speed = self.scene.engine.hass.client.get_entity(
                entity_id=self.entity_wind_speed
            )
            wind_bearing = self.scene.engine.hass.client.get_entity(
                entity_id=self.entity_wind_bearing
            )
            condition = self.scene.engine.hass.client.get_entity(
                entity_id=self.entity_condition
            )
            temp = self.scene.engine.hass.client.get_entity(entity_id=self.entity_temp)
            forecast_precipitation = self.scene.engine.hass.client.get_entity(
                entity_id=self.entity_forecast_precipitation
            )
            self.weather = dict(
                sun=sun.state.state,
                weather_code=int(weather_code.state.state),
                condition=condition.state.state,
                wind_speed=float(wind_speed.state.state),
                wind_bearing=float(wind_bearing.state.state),
                temp=float(temp.state.state),
                forecast_precipitation=float(forecast_precipitation.state.state),
            )
            logger.debug(
                f"updated: sun={self.weather['sun']} weather_code={self.weather['weather_code']} condition={self.weather['condition']} wind_speed={self.weather['wind_speed']} wind_bearing={self.weather['wind_bearing']} temp={self.weather['temp']} forecast_precipitation={self.weather['forecast_precipitation']}"
            )
        except Exception as e:
            logger.warn(f"Error updating weather: {e}")

    def cache_image(self, name: str) -> None:
        if name not in self.image_cache:
            self.image_cache[name] = list()
            for i in range(0, 60):
                filename = os.path.join(
                    self.image_path,
                    "animated",
                    name,
                    f"{name}_{i:05}.png",
                )

                if os.path.exists(filename):
                    image = load_image(filename)
                    scaled = scale_surface(
                        image, Vector2(self.rect.width, self.rect.width)  # squared
                    )
                    self.image_cache[name].append(scaled)

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if not self.weather:
            return
        try:
            # Background
            self.image.blit(self._render_background(), (0, -32))
            # Temperature
            self.image.blit(self.surface_temp, (0, 0))
            # Wind
            self.image.blit(self.surface_wind, (0, 32))
            # Rain probability
            if (
                self.weather["forecast_precipitation"]
                > RAIN_PROBABILITY_DISPLAY_THRESHOLD
            ):
                self.image.blit(
                    self.surface_rain_prob,
                    (64 - self.surface_rain_prob.get_width(), -1),
                )
        except Exception as e:
            logger.warn(f"error rendering weather: {e}", exc_info=e)

    def _render_background(self) -> pygame.Surface:
        images = convert_weather_code_to_image_name(self.weather["weather_code"])
        image_name = images[1 if self.weather["sun"] == "above_horizon" else 2]
        self.cache_image(image_name)
        frame_count = len(self.image_cache[image_name])
        self.image_frame = (self.image_frame + 1) % frame_count
        if frame_count > 1:
            self.dirty = 1
        return self.image_cache[image_name][self.image_frame]

    def _render_temperature(self, font_size: int = 24) -> pygame.Surface:
        label = (
            f"{int(self.weather['temp'])}" if self.weather["temp"] is not None else "?"
        )
        temp_text = render_text(
            label,
            "fonts/bitstream-vera.ttf",
            font_size,
            color_fg=Color(255, 255, 255, 255),
            color_outline=Color(0, 0, 0, 255),
        )
        surface = Surface(
            (temp_text.get_width() + 20, temp_text.get_height()), SRCALPHA
        )
        surface.blit(temp_text, (0, -4))
        degree_text = render_text(
            "°",
            "fonts/bitstream-vera.ttf",
            16,
            color_fg=self.color_temp,
            color_outline=Color(0, 0, 0, 255),
        )
        surface.blit(degree_text, (temp_text.get_width() - 4, -2))
        return surface

    def _render_precipitation(self) -> Surface:
        label = (
            f"{int(self.weather['forecast_precipitation'])}%"
            if self.weather["forecast_precipitation"] is not None
            else "?"
        )
        return render_text(
            label,
            "fonts/bitstream-vera.ttf",
            8,
            color_fg=self.color_rain_prob,
            color_outline=Color(0, 0, 0, 255),
        )

    def _render_wind(self) -> Surface:
        surface = pygame.Surface((32, 32), SRCALPHA)
        angle = self.weather["wind_bearing"]
        speed = int(convert_ms_to_mph(self.weather["wind_speed"]))
        arrow = render_arrow((4, 4), 12, angle, Color(0, 0, 0, 192), adjust=180)
        surface.blit(arrow, (2, 4))
        speed_str = f"{speed}"
        label = render_text(
            speed_str,
            "fonts/bitstream-vera.ttf",
            9,
            self.color_wind,
            color_outline=Color(0, 0, 0, 255),
        )
        surface.blit(label, (14 - (label.get_width() / 2), 9))
        return surface


def convert_weather_code_to_image_name(weather_code: int) -> List[str]:
    return IMAGE_MAPPING[weather_code]


def convert_ms_to_mph(ms: float) -> float:
    return ms * 2.23694
