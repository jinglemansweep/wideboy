import logging
import pygame
from pygame import Surface
from pygame.math import Vector2
from typing import Any, Optional
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import settings, matrix_options
from wideboy.constants import EVENT_HASS_ENTITY_UPDATE
from wideboy.utils.helpers import post_event, bool_to_hass_state

logger = logging.getLogger("display")


class Display:
    matrix: Optional[RGBMatrix] = None
    buffer: Optional[Any] = None
    visible: bool = True

    def __init__(self):
        logger.debug(
            f"display:init \
              canvas=({settings.display.canvas.width}x{settings.display.canvas.height} \
              matrix_enabled={settings.display.matrix.enabled}"
        )
        if settings.display.matrix.enabled:
            self.matrix = RGBMatrix(options=matrix_options)
            self.buffer = self.matrix.CreateFrameCanvas()
        self.black = build_black_surface(
            (
                settings.display.canvas.width,
                settings.display.canvas.height,
            )
        )

    def set_visible(self, state: bool) -> None:
        logger.debug(f"display:visible state={state}")
        post_event(
            EVENT_HASS_ENTITY_UPDATE,
            name="master",
            state=dict(state=bool_to_hass_state(state)),
        )
        self.visible = state

    def set_brightness(self, brightness: int) -> None:
        logger.debug(f"display:brightness brightness={brightness}")
        if settings.display.matrix.enabled and self.matrix is not None:
            self.matrix.brightness = (brightness / 255) * 100
        post_event(
            EVENT_HASS_ENTITY_UPDATE,
            name="master",
            state=dict(state=bool_to_hass_state(self.visible), brightness=brightness),
        )

    def render(self, surface: Surface, is_updates: bool = False):
        if not settings.display.matrix.enabled:
            return
        surface = surface if self.visible else self.black
        if self.buffer is not None and self.matrix is not None:
            if is_updates:
                self.buffer.SetImage(surface_to_led_matrix(surface))
            self.matrix.SwapOnVSync(self.buffer)


def surface_to_led_matrix(surface: Surface) -> Image.Image:
    pixels = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", (surface.get_width(), surface.get_height()), pixels)


def build_black_surface(size: Vector2):
    surface = Surface(size)
    surface.fill(0)
    return surface
