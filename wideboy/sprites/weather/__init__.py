import logging
import os
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    load_image,
    pil_to_surface,
)
from wideboy.constants import EVENT_EPOCH_SECOND
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
            if event.type == EVENT_EPOCH_SECOND and event.unit % 10 == 0:
                self.render()

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if STATE.weather_summary is not None:
            icon_filename = os.path.join(
                settings.paths.images_weather, f"{STATE.weather_summary}.png"
            )
            self.icon_summary = pygame.transform.scale(
                load_image(icon_filename), (48, 48)
            )
            self.image.blit(self.icon_summary, (-4, -8))
        if STATE.temperature is not None:
            temp_str = (
                f"{int(round(STATE.temperature, 0))}"
                if STATE.temperature is not None
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
            STATE.rain_probability is not None
            and STATE.rain_probability > RAIN_PROBABILITY_DISPLAY_THRESHOLD
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
