import pygame
from typing import Any
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import MATRIX_SIZE, MATRIX_PANEL_SIZE, matrix_options


def setup_led_matrix() -> tuple[RGBMatrix, Any]:
    matrix = RGBMatrix(options=matrix_options)
    buffer = matrix.CreateFrameCanvas()
    return matrix, buffer


def render_led_matrix(
    matrix: RGBMatrix, surface: pygame.surface.Surface, buffer: Any
) -> Any:
    temp_surface = wrap_surface(
        surface, MATRIX_SIZE, MATRIX_PANEL_SIZE
    )  # numpy arrays might be faster than pygame blitting
    with pygame.surfarray.pixels3d(temp_surface) as pixels:
        buffer.SetImage(pixels)
    # Flip and return next buffer
    return matrix.SwapOnVSync(buffer)


def wrap_surface(
    surface: pygame.surface.Surface,
    shape: tuple[int, int],
    tile_size: tuple[int, int],
) -> pygame.surface.Surface:
    temp_surface = pygame.Surface(shape)
    x_tiles = shape[0] // tile_size[0]
    y_tiles = shape[1] // tile_size[1]
    row = 0
    while row <= y_tiles:
        y = row * tile_size[1]
        x = tile_size[0] * (x_tiles * row)
        temp_surface.blit(
            surface,
            (0, y),
            (x, 0, tile_size[0] * x_tiles, tile_size[1] * 1),
        )
        row += 1
    return temp_surface
