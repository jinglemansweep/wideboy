import logging
import numpy as np
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

    def render(
        self,
        surface: Surface,
    ):
        if not settings.display.matrix.enabled:
            return
        surface = surface if self.visible else self.black
        pixels = pygame.surfarray.pixels3d(surface)
        if settings.display.matrix.wrap_surface:
            wrapped = self.wrap_surface(
                pixels,
                Vector2(
                    settings.display.matrix.width,
                    settings.display.matrix.height,
                ),
            )
            image = Image.fromarray(wrapped).convert("RGB")
        else:
            image = Image.fromarray(pixels).convert("RGB")
        if self.buffer is not None and self.matrix is not None:
            self.buffer.SetImage(image)
            self.matrix.SwapOnVSync(self.buffer)

    def wrap_surface(self, array: Any, new_shape: Vector2) -> Any:
        row_size = array.shape[1]
        cols = int(new_shape[0])
        rows = int(new_shape[1]) // row_size
        reshaped = np.full((cols, rows * row_size, 3), 0, dtype=np.uint8)
        for ri in range(rows):
            row_offset = ri * row_size
            col_offset = ri * cols
            reshaped[0:cols, row_offset : row_offset + row_size] = array[
                col_offset : col_offset + cols, 0:row_size
            ]
        return reshaped


def surface_to_led_matrix(surface: Surface) -> Image.Image:
    pixels = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", (surface.get_width(), surface.get_height()), pixels)


def build_black_surface(size: Vector2):
    surface = Surface(size)
    surface.fill(0)
    return surface
