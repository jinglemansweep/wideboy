import logging
import os
import pygame
import random
from typing import Optional
from pygame import SRCALPHA
from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    load_image,
    scale_surface,
    pil_to_surface,
)
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_EPOCH_SECOND
from wideboy.config import settings

logger = logging.getLogger("sprite.weather")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    mapping = {
        200: [
            "thunderstorm with light rain",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        201: [
            "thunderstorm with rain",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        202: [
            "thunderstorm with heavy rain",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        210: [
            "light thunderstorm",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        211: [
            "thunderstorm",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        212: [
            "heavy thunderstorm",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        221: [
            "ragged thunderstorm",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        230: [
            "thunderstorm with light drizzle",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        231: [
            "thunderstorm with drizzle",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        232: [
            "thunderstorm with heavy drizzle",
            "wsymbol_0024_thunderstorms",
            "wsymbol_0040_thunderstorms_night",
        ],
        300: [
            "light intensity drizzle",
            "wsymbol_0048_drizzle",
            "wsymbol_0066_drizzle_night",
        ],
        301: ["drizzle", "wsymbol_0048_drizzle", "wsymbol_0066_drizzle_night"],
        302: [
            "heavy intensity drizzle",
            "wsymbol_0081_heavy_drizzle",
            "wsymbol_0082_heavy_drizzle_night",
        ],
        310: [
            "light intensity drizzle rain",
            "wsymbol_0048_drizzle",
            "wsymbol_0066_drizzle_night",
        ],
        311: ["drizzle rain", "wsymbol_0048_drizzle", "wsymbol_0066_drizzle_night"],
        312: [
            "heavy intensity drizzle rain",
            "wsymbol_0081_heavy_drizzle",
            "wsymbol_0082_heavy_drizzle_night",
        ],
        321: [
            "shower drizzle",
            "wsymbol_0009_light_rain_showers",
            "wsymbol_0025_light_rain_showers_night",
        ],
        500: [
            "light rain",
            "wsymbol_0017_cloudy_with_light_rain",
            "wsymbol_0033_cloudy_with_light_rain_night",
        ],
        501: [
            "moderate rain",
            "wsymbol_0017_cloudy_with_light_rain",
            "wsymbol_0033_cloudy_with_light_rain_night",
        ],
        502: [
            "heavy intensity rain",
            "wsymbol_0018_cloudy_with_heavy_rain",
            "wsymbol_0034_cloudy_with_heavy_rain_night",
        ],
        503: [
            "very heavy rain",
            "wsymbol_0018_cloudy_with_heavy_rain",
            "wsymbol_0034_cloudy_with_heavy_rain_night",
        ],
        504: [
            "extreme rain",
            "wsymbol_0051_extreme_rain",
            "wsymbol_0069_extreme_rain_night",
        ],
        511: [
            "freezing rain",
            "wsymbol_0050_freezing_rain",
            "wsymbol_0068_freezing_rain_night",
        ],
        520: [
            "light intensity shower rain",
            "wsymbol_0009_light_rain_showers",
            "wsymbol_0025_light_rain_showers_night",
        ],
        521: [
            "shower rain",
            "wsymbol_0009_light_rain_showers",
            "wsymbol_0025_light_rain_showers_night",
        ],
        522: [
            "heavy intensity shower rain",
            "wsymbol_0010_heavy_rain_showers",
            "wsymbol_0026_heavy_rain_showers_night",
        ],
        600: [
            "light snow",
            "wsymbol_0019_cloudy_with_light_snow",
            "wsymbol_0035_cloudy_with_light_snow_night",
        ],
        601: [
            "snow",
            "wsymbol_0019_cloudy_with_light_snow",
            "wsymbol_0035_cloudy_with_light_snow_night",
        ],
        602: [
            "heavy snow",
            "wsymbol_0020_cloudy_with_heavy_snow",
            "wsymbol_0036_cloudy_with_heavy_snow_night",
        ],
        611: [
            "sleet",
            "wsymbol_0021_cloudy_with_light_sleet",
            "wsymbol_0037_cloudy_with_sleet_night",
        ],
        621: [
            "shower snow",
            "wsymbol_0011_light_snow_showers",
            "wsymbol_0027_light_snow_showers_night",
        ],
        701: ["mist", "wsymbol_0006_mist", "wsymbol_0063_mist_night"],
        711: ["smoke", "wsymbol_0055_smoke", "wsymbol_0073_smoke_night"],
        721: ["haze", "wsymbol_0005_hazy_sun", "wsymbol_0041_partly_cloudy_night"],
        731: [
            "sand, dust whirls",
            "wsymbol_0056_dust_sand",
            "wsymbol_0074_dust_sand_night",
        ],
        741: ["fog", "wsymbol_0007_fog", "wsymbol_0064_fog_night"],
        800: ["sky is clear", "wsymbol_0001_sunny", "wsymbol_0008_clear_sky_night"],
        801: [
            "few clouds",
            "wsymbol_0002_sunny_intervals",
            "wsymbol_0041_partly_cloudy_night",
        ],
        802: [
            "scattered clouds",
            "wsymbol_0002_sunny_intervals",
            "wsymbol_0041_partly_cloudy_night",
        ],
        803: [
            "broken clouds",
            "wsymbol_0043_mostly_cloudy",
            "wsymbol_0044_mostly_cloudy_night",
        ],
        804: [
            "overcast clouds",
            "wsymbol_0004_black_low_cloud",
            "wsymbol_0042_cloudy_night",
        ],
        900: ["tornado", "wsymbol_0079_tornado", "wsymbol_0079_tornado"],
        901: [
            "tropical storm",
            "wsymbol_0080_tropical_storm_hurricane",
            "wsymbol_0080_tropical_storm_hurricane",
        ],
        902: [
            "hurricane",
            "wsymbol_0080_tropical_storm_hurricane",
            "wsymbol_0080_tropical_storm_hurricane",
        ],
        903: ["cold", "wsymbol_0046_cold", "wsymbol_0062_cold_night"],
        904: ["hot", "wsymbol_0045_hot", "wsymbol_0061_hot_night"],
        905: ["windy", "wsymbol_0060_windy", "wsymbol_0078_windy_night"],
        906: [
            "hail",
            "wsymbol_0023_cloudy_with_heavy_hail",
            "wsymbol_0039_cloudy_with_heavy_hail_night",
        ],
    }

    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 0),
        color_temp: pygame.color.Color = (255, 255, 255, 255),
        color_rain_prob: pygame.color.Color = (255, 255, 0, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_temp = color_temp
        self.color_rain_prob = color_rain_prob
        self.icon_summary = None
        self.entity_weather_code = "sensor.openweathermap_weather_code"
        self.entity_condition = "sensor.openweathermap_condition"
        self.entity_temp = "sensor.openweathermap_temperature"
        self.entity_forecast_precipitation = (
            "sensor.openweathermap_forecast_precipitation_probability"
        )
        self.icon_cache = dict()
        self.icon_frame = 0
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
            if event.type == EVENT_EPOCH_SECOND and event.unit % 1 == 0:
                self.weather["weather_code"] = random.choice(list(self.mapping.keys()))
        self.render()

    def update_state(self) -> None:
        try:
            sun = HASS.get_entity(entity_id="sun.sun")
            weather_code = HASS.get_entity(entity_id=self.entity_weather_code)
            condition = HASS.get_entity(entity_id=self.entity_condition)
            temp = HASS.get_entity(entity_id=self.entity_temp)
            forecast_precipitation = HASS.get_entity(
                entity_id=self.entity_forecast_precipitation
            )
            self.weather = dict(
                sun=sun.state.state,
                weather_code=int(weather_code.state.state),
                condition=condition.state.state,
                temp=float(temp.state.state),
                forecast_precipitation=float(forecast_precipitation.state.state),
            )
            logger.debug(
                f"updated: sun={self.weather['sun']} weather_code={self.weather['weather_code']} condition={self.weather['condition']} temp={self.weather['temp']} forecast_precipitation={self.weather['forecast_precipitation']}"
            )
        except Exception as e:
            logger.warn(f"Error updating weather: {e}")

    def cache_icon_sprites(self, icon_name: str) -> None:
        if icon_name not in self.icon_cache:
            self.icon_cache[icon_name] = list()
            for i in range(0, 60):
                icon_filename = os.path.join(
                    settings.paths.images_weather,
                    "premium",
                    "animated",
                    icon_name,
                    f"{icon_name}_{i:05}.png",
                )
                if os.path.exists(icon_filename):
                    icon_surface = load_image(icon_filename)
                    self.icon_cache[icon_name].append(
                        scale_surface(icon_surface, (self.rect.width, self.rect.height))
                    )

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if self.weather is not None:
            # Icon
            icon_mapping = self.condition_to_icon(self.weather["weather_code"])
            icon_name = icon_mapping[1 if self.weather["sun"] == "above_horizon" else 2]
            # icon_name = "wsymbol_0013_sleet_showers"
            if os.path.exists(
                os.path.join(
                    settings.paths.images_weather, "premium", "animated", icon_name
                )
            ):
                self.cache_icon_sprites(icon_name)
                self.icon_frame = (self.icon_frame + 1) % len(
                    self.icon_cache[icon_name]
                )
                self.image.blit(self.icon_cache[icon_name][self.icon_frame], (0, 0))
                self.dirty = 1
            # Temperature
            temp_str = (
                f"{int(self.weather['temp'])}"
                if self.weather["temp"] is not None
                else "?"
            )
            temperature_text = render_text(
                temp_str,
                "fonts/molot.otf",
                32,
                pygame.Color(255, 255, 255),
                (0, 0, 0, 0),
                (0, 0, 0, 0),
            )
            self.image.blit(temperature_text, (0, 30))
            degree_text = render_text(
                "°",
                "fonts/bitstream-vera.ttf",
                16,
                self.color_temp,
                (0, 0, 0, 0),
                (0, 0, 0, 0),
            )
            self.image.blit(degree_text, (temperature_text.get_width() - 4, 32))
            if (
                self.weather["forecast_precipitation"]
                > RAIN_PROBABILITY_DISPLAY_THRESHOLD
            ):
                rain_prob_str = (
                    f"{int(self.weather['forecast_precipitation'])}%"
                    if self.weather["forecast_precipitation"] is not None
                    else "?"
                )
                rain_prob_text = render_text(
                    rain_prob_str,
                    "fonts/bitstream-vera.ttf",
                    8,
                    self.color_rain_prob,
                )
                self.image.blit(rain_prob_text, (64 - rain_prob_text.get_width(), 53))
        self.dirty = 1

    def condition_to_icon(self, condition: int) -> tuple[str, str, str]:
        return self.mapping[condition]
