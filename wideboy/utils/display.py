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
    wrapped = wrap_surface(surface, MATRIX_SIZE, MATRIX_PANEL_SIZE)
    pixels = pygame.surfarray.pixels3d(wrapped)
    image = Image.fromarray(pixels)
    buffer.SetImage(image)
    # Flip and return next buffer
    return matrix.SwapOnVSync(buffer)


def blank_surface(size: tuple[int, int]):
    surface = pygame.surface.Surface(size)
    surface.fill(0)
    return surface


def wrap_surface_array(
    array: np.ndarray,
    canvas_shape: tuple[int, int],
) -> np.array:
    # FIXME: VERY BROKEN
    wrapped = np.ndarray((canvas_shape[0], canvas_shape[1], 3), dtype=np.uint8)
    print(f"array={array.shape} wrapped={wrapped.shape}")

    wrapped = np.append(wrapped, array[0:256, 0:64, 0:3], axis=1)
    # wrapped[64:0, 128:256] = array[0:256, 64:512]
    # wrapped[128:0, 128:256] = array[0:256, 64:768]
    return wrapped
    """
    width = array.shape[0] // canvas_shape[0]
    row_height = array.shape[1]
    print(f"width={width} row_height={row_height}")
    row = 0
    while row < width:
        xa = row * canvas_shape[0]
        ya = 0
        xb = xa + canvas_shape[0]
        yb = row_height
        slice = array[ya:xa, yb:xb]
        print(row, "SLICE", slice.shape, wrapped.shape)
        # print(f"row={row}: slice={xa}:{ya} -> {xb}:{yb}")
        wrapped = np.append(wrapped, slice)
        row += 1
    print(wrapped.shape)
    return array
    """


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
