import logging
import numpy as np
import pygame
import sys
from dynaconf import Dynaconf
from pygame import Surface
from pygame.math import Vector2
from typing import Any, Optional
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore


logger = logging.getLogger("controller.display")


class Display:
    matrix: Optional[RGBMatrix] = None
    buffer: Optional[Any] = None

    def __init__(self, options: Dynaconf):
        self.options = options
        logger.debug(
            f"Display: canvas=({options.canvas.width}x{options.canvas.height} matrix_enabled={options.matrix.enabled} matrix_size=({options.matrix.width}x{options.matrix.height})"
        )
        if self.options.matrix.enabled:
            self.matrix = RGBMatrix(options=self.options.matrix.driver)
            self.buffer = self.matrix.CreateFrameCanvas()

    def render(
        self,
        surface: Surface,
    ) -> Any:
        if not self.options.matrix.enabled:
            return
        pixels = pygame.surfarray.pixels3d(surface)
        wrapped = self.wrap_surface(
            pixels, (self.options.matrix.width, self.options.matrix.height)
        )
        image = Image.fromarray(wrapped).convert("RGB")
        self.buffer.SetImage(image)
        return self.matrix.SwapOnVSync(self.buffer)

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
