import logging
import pygame
from typing import Optional
from pygame import SRCALPHA
from wideboy.sprites import BaseSprite
from wideboy.utils.images import render_text, load_resize_image
from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)


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
        self.icon_rain = load_resize_image("images/icons/rain_prob.png", (16, 16))
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
            f"{int(round(state.temperature, 0))}°C"
            if state.temperature is not None
            else "?"
        )
        rain_prob_str = (
            f"{state.rain_probability}%" if state.rain_probability is not None else "?"
        )
        self.image.fill(self.color_bg)
        temperature_text = render_text(
            temp_str,
            "bitstreamverasans",
            20,
            self.color_temp,
            (0, 0, 0, 255),
        )
        self.image.blit(temperature_text, (4, -1))
        self.image.blit(self.icon_rain, (55, 2))
        rain_prob_text = render_text(
            rain_prob_str,
            "bitstreamverasans",
            16,
            self.color_rain_prob,
            (0, 0, 0, 255),
        )
        self.image.blit(rain_prob_text, (72, 1))
