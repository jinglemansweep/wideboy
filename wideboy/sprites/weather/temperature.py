import logging
import pygame
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import Tuple
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_text
from wideboy.constants import EVENT_EPOCH_MINUTE

logger = logging.getLogger("sprite.weather.temp")


class WeatherTemperatureSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        font_name: str = "fonts/molot.otf",
        font_size: int = 16,
        font_padding: int = 0,
        entity_temp: str = "sensor.openweathermap_temperature",
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.font_name = font_name
        self.font_size = font_size
        self.font_padding = font_padding
        self.entity_temp = entity_temp
        self.update_state()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                self.update_state()

    def update_state(self) -> None:
        try:
            # self.image = self.build_surface(temp)
            # self.dirty = 1
            pass
        except Exception as e:
            logger.error("state:error", exc_info=e)

    def build_surface(
        self,
        temp: float,
    ) -> Surface:
        surface = Surface((self.rect.width, self.rect.height), SRCALPHA)
        color_fg, color_bg, color_outline = temp_to_colors(temp)
        pygame.draw.circle(surface, color_bg, surface.get_rect().center, 12)
        pygame.draw.circle(surface, color_outline, surface.get_rect().center, 12, 1)
        temp_str = f"{int(temp)}"
        logger.debug(f"surface:build temp={temp_str}")
        label = render_text(
            temp_str,
            self.font_name,
            self.font_size,
            color_fg=color_fg,
            color_outline=color_outline,
        )
        surface.blit(
            label,
            ((self.rect.width / 2) - (label.get_width() / 2), 3 + self.font_padding),
        )
        return surface


def temp_to_colors(temp: float) -> Tuple[Color, Color, Color]:
    if temp < 1.0:
        return Color(255, 255, 255, 255), Color(0, 0, 255, 255), Color(0, 0, 0, 255)
    elif temp < 8.0:
        return Color(255, 255, 255, 255), Color(64, 64, 255, 255), Color(0, 0, 0, 255)
    elif temp < 15.0:
        return Color(255, 255, 255, 255), Color(255, 255, 0, 255), Color(0, 0, 0, 255)
    elif temp < 20.0:
        return Color(255, 255, 255, 255), Color(255, 192, 0, 255), Color(0, 0, 0, 255)
    elif temp < 25.0:
        return Color(255, 255, 255, 255), Color(255, 128, 0, 255), Color(0, 0, 0, 255)
    elif temp < 30.0:
        return Color(255, 255, 255, 255), Color(255, 64, 0, 255), Color(0, 0, 0, 255)
    elif temp >= 30.0:
        return Color(255, 255, 255, 255), Color(255, 0, 0, 255), Color(0, 0, 0, 255)
    else:
        return Color(255, 255, 255, 255), Color(64, 64, 64, 255), Color(0, 0, 0, 255)
