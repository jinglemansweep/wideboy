import logging
import numpy as np
import pygame
import sys
from dynaconf import Dynaconf
from pygame import Surface
from pygame.math import Vector2
from typing import Any, Optional, TYPE_CHECKING
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import settings, matrix_options

logger = logging.getLogger("display")


class Display:
    matrix: Optional[RGBMatrix] = None
    buffer: Optional[Any] = None

    def __init__(self):
        logger.debug(
            f"display:init canvas=({settings.display.canvas.width}x{settings.display.canvas.height} matrix_enabled={settings.display.matrix.enabled} matrix_size=({settings.display.matrix.width}x{settings.display.matrix.height})"
        )
        if settings.display.matrix.enabled:
            self.matrix = RGBMatrix(options=matrix_options)
            self.buffer = self.matrix.CreateFrameCanvas()

    def render(
        self,
        surface: Surface,
    ):
        if not settings.display.matrix.enabled:
            return
        pixels = pygame.surfarray.pixels3d(surface)
        wrapped = self.wrap_surface(
            pixels,
            (
                settings.display.matrix.width,
                settings.display.matrix.height,
            ),
        )
        image = Image.fromarray(wrapped).convert("RGB")
        self.buffer.SetImage(image)
        self.matrix.SwapOnVSync(self.buffer)

    def blank_surface(size: Vector2):
        surface = Surface(size)
        surface.fill(0)
        return surface

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
