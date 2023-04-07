import logging
import os
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    load_image,
    pil_to_surface,
)
from wideboy.constants import EVENT_EPOCH_MINUTE
from wideboy.state import STATE
from wideboy.config import settings

logger = logging.getLogger("sprite.weather")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 0),
        color_temp: pygame.color.Color = (255, 255, 255, 255),
        color_rain_prob: pygame.color.Color = (255, 255, 0, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.font_temp = pygame.font.SysFont("", 20)
        self.color_bg = color_bg
        self.color_temp = color_temp
        self.color_rain_prob = color_rain_prob
        self.icon_summary = None
        self.entity_condition = "sensor.openweathermap_condition"
        self.entity_temp = "sensor.openweathermap_temperature"
        self.entity_forecast_precipitation = (
            "sensor.openweathermap_forecast_precipitation_probability"
        )
        self.weather = None
        self.update_state()
        self.render()

    def update(
        self,
        frame: str,
        clock: pygame.time.Clock,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE or self.weather is None:
                self.update_state()

    def update_state(self) -> None:
        try:
            condition = HASS.get_entity(entity_id=self.entity_condition)
            temp = HASS.get_entity(entity_id=self.entity_temp)
            forecast_precipitation = HASS.get_entity(
                entity_id=self.entity_forecast_precipitation
            )
            self.weather = dict(
                condition=condition.state.state,
                temp=float(temp.state.state),
                forecast_precipitation=float(forecast_precipitation.state.state),
            )
            logger.debug(
                f"updated: condition={self.weather['condition']} temp={self.weather['temp']} forecast_precipitation={self.weather['forecast_precipitation']}"
            )
            self.render()
        except Exception as e:
            logger.warn(f"Error updating weather: {e}")

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if self.weather is not None:
            # Icon
            icon_name = condition_to_icon(self.weather["condition"])
            icon_filename = os.path.join(
                settings.paths.images_weather, f"{icon_name}.png"
            )
            self.icon_summary = pygame.transform.scale(
                load_image(icon_filename), (48, 48)
            )
            self.image.blit(self.icon_summary, (-4, -8))
            # Temperature
            temp_str = (
                f"{int(self.weather['temp'])}"
                if self.weather["temp"] is not None
                else "?"
            )
            temperature_text = render_text(
                temp_str,
                "fonts/bitstream-vera.ttf",
                16,
                self.color_temp,
                (0, 0, 0, 0),
                (0, 0, 0, 0),
            )
            self.image.blit(temperature_text, (36, 0))
            degree_text = render_text(
                "°",
                "fonts/bitstream-vera.ttf",
                16,
                self.color_temp,
                (0, 0, 0, 0),
                (0, 0, 0, 0),
            )
            self.image.blit(degree_text, (32 + temperature_text.get_width(), -1))
            if (
                self.weather["forecast_precipitation"]
                > RAIN_PROBABILITY_DISPLAY_THRESHOLD
            ):
                rain_prob_str = (
                    f"{STATE.rain_probability}%"
                    if STATE.rain_probability is not None
                    else "?"
                )
                rain_prob_text = render_text(
                    rain_prob_str,
                    "fonts/bitstream-vera.ttf",
                    10,
                    self.color_rain_prob,
                )
                self.image.blit(rain_prob_text, (63 - rain_prob_text.get_width(), 15))
        self.dirty = 1


def condition_to_icon(condition: int) -> str:
    icon: str = None
    if condition == "clear-night":
        icon = "night"
    elif condition == "cloudy":
        icon = "cloudy"
    elif condition == "exceptional":
        icon = "exceptional"
    elif condition == "fog":
        icon = "fog"
    elif condition == "hail":
        icon = "hail"
    elif condition == "lightning":
        icon = "thunderstorms"
    elif condition == "lightning-rainy":
        icon = "thunderstorms-2"
    elif condition == "partlycloudy":
        icon = "clear-cloudy"
    elif condition == "pouring":
        icon = "drizzle"
    elif condition == "rainy":
        icon = "drizzle"
    elif condition == "snowy":
        icon = "snow"
    elif condition == "snowy-rainy":
        icon = "sleet"
    elif condition == "sunny":
        icon = "sunny"
    elif condition == "windy":
        icon = "windy"
    elif condition == "windy-variant":
        icon = "windy"
    return icon
