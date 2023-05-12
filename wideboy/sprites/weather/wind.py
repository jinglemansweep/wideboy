import logging
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA

# from wideboy.mqtt.homeassistant import HASS
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_arrow, render_text
from wideboy.constants import EVENT_EPOCH_MINUTE

logger = logging.getLogger("sprite.weather.wind")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherWindSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        arrow_size: int = 16,
        color_fg: Color = Color(255, 255, 255, 255),
        color_outline: Color = Color(0, 0, 0, 255),
        color_arrow: Color = Color(0, 0, 0, 255),
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 9,
        font_padding: int = 2,
        entity_wind_direction: str = "sensor.openweathermap_wind_bearing",
        entity_wind_speed: str = "sensor.openweathermap_wind_speed",
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.arrow_size = arrow_size
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.color_arrow = color_arrow
        self.font_name = font_name
        self.font_size = font_size
        self.font_padding = font_padding
        self.entity_wind_direction = entity_wind_direction
        self.entity_wind_speed = entity_wind_speed
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
            with self.scene.engine.hass.client as hass:
                wind_direction = int(
                    hass.get_state(entity_id=self.entity_wind_direction).state
                )
                wind_speed = float(
                    hass.get_state(entity_id=self.entity_wind_speed).state
                )
            logger.debug(
                f"weather:wind:state direction={wind_direction} speed={wind_speed}"
            )
            self.image = self.build_surface(wind_direction, wind_speed)
            self.dirty = 1
        except Exception as e:
            logger.error("weather:wind:state:error", exc_info=e)

    def build_surface(
        self,
        direction: int,
        speed: float,
    ) -> Surface:
        surface = Surface((self.rect.width, self.rect.height), SRCALPHA)
        arrow = render_arrow((4, 4), 12, direction, Color(0, 0, 0, 192), adjust=180)
        surface.blit(arrow, (2, 4))
        speed = int(convert_ms_to_mph(speed))
        speed_str = f"{speed}"
        logger.debug(f"surface:build direction={direction} speed={speed}")
        label = render_text(
            speed_str,
            self.font_name,
            self.font_size,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )
        label_offset = (-2, 0)
        surface.blit(
            label,
            (
                (self.rect.width / 2) - (label.get_width() / 2) + label_offset[0],
                8 + self.font_padding + label_offset[1],
            ),
        )
        return surface


def convert_ms_to_mph(ms: float) -> float:
    return ms * 2.23694
