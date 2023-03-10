import logging
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.sprites._base import BaseSprite
from wideboy.utils.images import render_text, load_resize_image
from wideboy.utils.pygame import EVENT_EPOCH_SECOND
from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        state: StateStore,
        color_bg: pygame.color.Color = (0, 0, 0, 192),
        color_temp: pygame.color.Color = (255, 255, 255, 255),
        color_rain_prob: pygame.color.Color = (255, 255, 0, 255),
    ) -> None:
        super().__init__(rect, state)
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
        if self.state.weather_summary is not None:
            icon_filename = f"images/icons/weather/{self.state.weather_summary}.png"
            self.icon_summary = load_resize_image(icon_filename, (72, 72))
            self.image.blit(self.icon_summary, (-4, -6))
        if self.state.temperature is not None:
            temp_str = (
                f"{int(round(self.state.temperature, 0))}"
                if self.state.temperature is not None
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
                "??",
                "fonts/bitstream-vera.ttf",
                20,
                self.color_temp,
                (0, 0, 0, 255),
            )
            self.image.blit(degree_text, (temperature_text.get_width() - 2, 29))
        if (
            self.state.rain_probability is not None
            and self.state.rain_probability > RAIN_PROBABILITY_DISPLAY_THRESHOLD
        ):
            rain_prob_str = (
                f"{self.state.rain_probability}%"
                if self.state.rain_probability is not None
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
