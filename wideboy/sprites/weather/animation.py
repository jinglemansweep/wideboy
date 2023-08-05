import logging
import os
import random
from pygame import Clock, Event, Rect, Surface, Vector2, SRCALPHA
from typing import Optional, List

# from wideboy.mqtt.homeassistant import HASS
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    load_image,
    scale_surface,
)
from wideboy.constants import EVENT_EPOCH_MINUTE, EVENT_EPOCH_SECOND
from wideboy.sprites.weather.resources import IMAGE_MAPPING

from wideboy.config import settings

logger = logging.getLogger("sprite.weather")

RAIN_PROBABILITY_DISPLAY_THRESHOLD = 25


class WeatherAnimationSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        size: Optional[Vector2] = None,
        demo: bool = False,
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.size = size or Vector2(self.rect.width, self.rect.height)
        self.demo = demo
        self.icon_summary = None
        self.entity_weather_code = "sensor.openweathermap_weather_code"
        self.entity_sun = "sun.sun"
        self.image_path = os.path.join(
            settings.paths.images_weather,
            "premium",
        )
        self.image_cache: dict[str, List[Surface]] = dict()
        self.image_frame = 0
        self.demo_index = 0
        self.weather_code: Optional[str] = None
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
            if event.type == EVENT_EPOCH_MINUTE:
                self.update_state()
            if event.type == EVENT_EPOCH_SECOND and event.unit % 10 == 0:
                self.dirty = 1

        if frame % 3 == 0:
            self.render()

    def update_state(self) -> None:
        try:
            if not self.demo:
                with self.scene.engine.hass.client as hass:
                    self.weather_daytime = (
                        hass.get_state(entity_id="sun.sun").state == "above_horizon"
                    )
                    self.weather_code = hass.get_state(
                        entity_id=self.entity_weather_code
                    ).state
            else:
                self.weather_daytime = random.choice([True, False])
                self.weather_code = str(random.choice(list(IMAGE_MAPPING.keys())))
            logger.debug(
                f"weather:state demo={self.demo} daytime={self.weather_daytime} code={self.weather_code}"
            )
        except Exception as e:
            logger.error("weather:background", exc_info=e)

    def cache_image(self, name: str) -> None:
        if name not in self.image_cache:
            self.image_cache[name] = list()
            frame_count = 0
            for i in range(0, 60):
                filename = os.path.join(
                    self.image_path,
                    "animated",
                    name,
                    f"{name}_{i:05}.png",
                )
                if os.path.exists(filename):
                    image = load_image(filename)
                    scaled = scale_surface(image, self.size)
                    self.image_cache[name].append(scaled)
                    frame_count += 1
            logger.debug(f"image:cache name={name} frames={frame_count}")

    def render(self) -> None:
        # self.weather_code = "600"
        if not self.weather_code:
            return
        images = convert_weather_code_to_image_name(self.weather_code)
        image_name = images[1 if self.weather_daytime else 2]
        self.cache_image(image_name)
        frame_count = len(self.image_cache[image_name])
        self.image_frame = (self.image_frame + 1) % frame_count
        # logger.debug(
        #     f"weather:render frame={self.image_frame}/{frame_count} name={image_name}"
        # )
        self.image = self.image_cache[image_name][self.image_frame]
        if frame_count > 1:
            self.dirty = 1


def convert_weather_code_to_image_name(weather_code: str) -> List[str]:
    return IMAGE_MAPPING[int(weather_code)]


def convert_ms_to_mph(ms: float) -> float:
    return ms * 2.23694
