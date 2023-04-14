import logging
import os
import pygame
import random
from typing import Optional
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    load_image,
    scale_surface,
    pil_to_surface,
)
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_EPOCH_SECOND
from wideboy.sprites.weather.resources import IMAGE_MAPPING
from wideboy.config import settings

logger = logging.getLogger("sprite.weather")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        color_bg: Color = Color(0, 0, 0, 0),
        color_temp: Color = Color(255, 255, 255, 255),
        color_rain_prob: Color = Color(255, 255, 0, 255),
        debug: bool = False,
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_temp = color_temp
        self.color_rain_prob = color_rain_prob
        self.debug = debug
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
        self.image_cache = dict()
        self.image_frame = 0
        self.weather = None
        self.update_state()
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
            if event.type == EVENT_EPOCH_MINUTE or self.weather is None:
                self.update_state()
            # if event.type == EVENT_EPOCH_SECOND and event.unit % 1 == 0:
            #    self.weather["weather_code"] = random.choice(list(self.mapping.keys()))
        self.render()

    def update_state(self) -> None:
        try:
            sun = HASS.get_entity(entity_id="sun.sun")
            weather_code = HASS.get_entity(entity_id=self.entity_weather_code)
            wind_speed = HASS.get_entity(entity_id=self.entity_wind_speed)
            wind_bearing = HASS.get_entity(entity_id=self.entity_wind_bearing)
            condition = HASS.get_entity(entity_id=self.entity_condition)
            temp = HASS.get_entity(entity_id=self.entity_temp)
            forecast_precipitation = HASS.get_entity(
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
                    scaled = scale_surface(image, (self.rect.width, self.rect.height))
                    self.image_cache[name].append(scaled)

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if not self.weather:
            return
        # Background
        self.image.blit(self._render_background(), (0, 0))
        # Temperature
        self.image.blit(self._render_temperature(), (0, 30))
        # Wind
        self.image.blit(self._render_wind(), (32, 32))
        # Rain probability
        if self.weather["forecast_precipitation"] > RAIN_PROBABILITY_DISPLAY_THRESHOLD:
            precip_surface = self._render_precipitation()
            self.image.blit(precip_surface, (64 - precip_surface.get_width(), 0))

    def _render_background(self) -> pygame.Surface:
        images = convert_weather_code_to_image_name(self.weather["weather_code"])
        image_name = images[1 if self.weather["sun"] == "above_horizon" else 2]
        if self.debug:
            image_name = "wsymbol_0013_sleet_showers"
        self.cache_image(image_name)
        frame_count = len(self.image_cache[image_name])
        self.image_frame = (self.image_frame + 1) % frame_count
        if frame_count > 1:
            self.dirty = 1
        return self.image_cache[image_name][self.image_frame]

    def _render_temperature(self) -> pygame.Surface:
        label = (
            f"{int(self.weather['temp'])}" if self.weather["temp"] is not None else "?"
        )
        temp_text = render_text(
            label,
            "fonts/bitstream-vera.ttf",
            32,
            pygame.Color(255, 255, 255),
        )
        surface = Surface(
            (temp_text.get_width() + 20, temp_text.get_height()), SRCALPHA
        )
        surface.blit(temp_text, (0, -2))
        degree_text = render_text(
            "°",
            "fonts/bitstream-vera.ttf",
            16,
            self.color_temp,
        )
        surface.blit(degree_text, (temp_text.get_width() - 4, 0))
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
            self.color_rain_prob,
        )

    def _render_wind(self) -> Surface:
        surface = pygame.Surface((32, 32), SRCALPHA)
        dir = convert_bearing_to_direction(self.weather["wind_bearing"])
        mph = int(convert_ms_to_mph(self.weather["wind_speed"]))
        pos = [0, 0]
        disc = load_image(
            os.path.join(
                self.image_path,
                "wind",
                "arrows",
                f"disc-{dir}.png",
            )
        )
        disc_scaled = scale_surface(disc, (32, 32))
        surface.blit(disc_scaled, pos)
        pygame.draw.circle(surface, (0, 0, 0), (pos[0] + 16, pos[1] + 16), 6)
        mph_str = f"{mph}"
        label = render_text(
            mph_str,
            "fonts/bitstream-vera.ttf",
            10,
            self.color_temp,
        )
        surface.blit(
            label,
            (
                pos[0] + 8 + (3 if len(mph_str) == 1 else 0),
                pos[1] + 8,
            ),
        )
        return surface


def convert_weather_code_to_image_name(weather_code: int) -> tuple[str, str, str]:
    return IMAGE_MAPPING[weather_code]


def convert_bearing_to_direction(bearing: float) -> str:
    if 0 < bearing < 45:
        return "sw"
    elif 45 <= bearing < 90:
        return "w"
    elif 90 <= bearing < 135:
        return "nw"
    elif 135 <= bearing < 180:
        return "n"
    elif 180 <= bearing < 225:
        return "ne"
    elif 225 <= bearing < 270:
        return "e"
    elif 270 <= bearing < 315:
        return "se"
    elif 315 <= bearing < 360:
        return "s"


def convert_ms_to_mph(ms: float) -> float:
    return ms * 2.23694
