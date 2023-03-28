import logging
import os
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    render_text,
    load_image,
    scale_image,
    pil_to_surface,
)
from wideboy.utils.pygame import EVENT_EPOCH_SECOND
from wideboy.state import STATE
from wideboy.config import settings

logger = logging.getLogger(__name__)

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 192),
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
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND and event.unit % 10 == 0:
                self.render()

    def render(self) -> None:
        self.image.fill(self.color_bg)
        if STATE.weather_summary is not None:
            icon_filename = os.path.join(
                settings.paths.images_icons, "weather", f"{STATE.weather_summary}.png"
            )
            self.icon_summary = scale_image(load_image(icon_filename), (72, 72))
            self.image.blit(pil_to_surface(self.icon_summary), (-4, -6))
        if STATE.temperature is not None:
            temp_str = (
                f"{int(round(STATE.temperature, 0))}"
                if STATE.temperature is not None
                else "?"
            )
            temperature_text = render_text(
                temp_str,
                "fonts/bitstream-vera.ttf",
                28,
                self.color_temp,
                (0, 0, 0, 255),
            )
            self.image.blit(temperature_text, (2, 29))
            degree_text = render_text(
                "°",
                "fonts/bitstream-vera.ttf",
                20,
                self.color_temp,
                (0, 0, 0, 255),
            )
            self.image.blit(degree_text, (temperature_text.get_width() - 2, 29))
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
                (0, 0, 0, 255),
            )
            self.image.blit(rain_prob_text, (62 - rain_prob_text.get_width(), -1))
        self.dirty = 1
