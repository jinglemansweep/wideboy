import numpy as np
import pygame
import sys
from typing import Any
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import CANVAS_SIZE, MATRIX_SIZE, MATRIX_PANEL_SIZE, matrix_options


def setup_led_matrix() -> tuple[RGBMatrix, Any]:
    matrix = RGBMatrix(options=matrix_options)
    buffer = matrix.CreateFrameCanvas()
    return matrix, buffer


def render_led_matrix(
    matrix: RGBMatrix, surface: pygame.surface.Surface, buffer: Any
) -> Any:
    pixels = pygame.surfarray.array3d(surface)
    wrapped = wrap_surface_array(pixels, MATRIX_SIZE)
    image = Image.fromarray(wrapped)
    buffer.SetImage(image)
    # Flip and return next buffer
    return matrix.SwapOnVSync(buffer)


def blank_surface(size: tuple[int, int]):
    surface = pygame.surface.Surface(size)
    surface.fill(0)
    return surface


def wrap_surface_array(
    array: np.ndarray,
    new_shape: tuple[int, int]
) -> np.array:
    row_size = array.shape[1]
    cols = new_shape[0]
    rows = new_shape[1] // row_size
    print(f"rows={rows} cols={cols} row_size={row_size}")
    reshaped = np.full((cols, rows * row_size, 3), 0, dtype=np.uint8)
    for ri in range(rows):
        row_offset = ri * row_size
        col_offset = ri * cols
        reshaped[0:cols, row_offset:row_offset+row_size] = array[col_offset:col_offset+cols, 0:row_size]
    return reshaped

def wrap_surface(
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


def wrap_surface_orig(
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
