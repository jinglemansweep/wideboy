import logging
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.sprites import BaseSprite
from wideboy.utils.images import render_text, load_resize_image
from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 128),
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
        self.dirty = 2
        self.render()

    def update(
        self,
        frame: str,
        delta: float,
        events: list[pygame.event.Event],
        state: StateStore,
    ) -> None:
        super().update(frame, delta, events, state)
        self.render(state)

    def render(self, state: Optional[StateStore] = None) -> None:
        if state is None:
            return
        temp_str = (
            f"{int(round(state.temperature, 0))}"
            if state.temperature is not None
            else "?"
        )
        rain_prob_str = (
            f"{state.rain_probability}%" if state.rain_probability is not None else "?"
        )
        self.image.fill(self.color_bg)
        if state.weather_summary is not None:
            icon_filename = f"images/icons/weather/{state.weather_summary}.png"
            self.icon_summary = load_resize_image(icon_filename, (64, 64))
            self.image.blit(self.icon_summary, (-8, -14))
        temperature_text = render_text(
            temp_str,
            "fonts/bitstream-vera.ttf",
            28,
            self.color_temp,
            (0, 0, 0, 255),
        )
        self.image.blit(temperature_text, (55 - temperature_text.get_width(), 26))
        if (
            state.rain_probability is not None
            and state.rain_probability > RAIN_PROBABILITY_DISPLAY_THRESHOLD
        ):
            rain_prob_text = render_text(
                rain_prob_str,
                "fonts/bitstream-vera.ttf",
                10,
                self.color_rain_prob,
                (0, 0, 0, 255),
            )
            self.image.blit(rain_prob_text, (56 - rain_prob_text.get_width(), 0))
