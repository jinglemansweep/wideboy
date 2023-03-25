import numpy as np
import pygame
import sys
from typing import Any, Optional
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore


class Display:
    matrix: Optional[RGBMatrix] = None
    buffer: Optional[Any] = None

    def __init__(self, options: Optional[dict]):
        self.options = options
        if self.options.get("enabled"):
            self.matrix = RGBMatrix(options=self.options.get("options"))
            self.buffer = self.matrix.CreateFrameCanvas()

    def render(self, surface: pygame.surface.Surface) -> Any:
        wrapped = self.wrap_surface(
            surface, self.options.get("size"), self.options.get("panel_size")
        )
        pixels = pygame.surfarray.pixels3d(wrapped)
        image = Image.fromarray(pixels)
        self.buffer.SetImage(image)
        self.buffer = self.matrix.SwapOnVSync(self.buffer)

    def wrap_surface(
        self,
        surface: pygame.surface.Surface,
        new_shape: tuple[int, int],
        tile_size: tuple[int, int],
    ) -> pygame.surface.Surface:
        temp_surface = pygame.Surface(new_shape)
        surface_width = surface.get_rect().width
        surface_height = surface.get_rect().height
        wrapped_width = new_shape[0]
        wrapped_row_count = surface_width // wrapped_width
        row = 0
        while row <= wrapped_row_count:
            y = row * surface_height
            x = wrapped_width * row
            temp_surface.blit(
                surface,
                (0, y),
                (x, 0, x + wrapped_width, surface_height),
            )
            row += 1
        return temp_surface
