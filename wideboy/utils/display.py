import numpy as np
import pygame
from typing import Any
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import settings, matrix_options

MATRIX_SIZE = pygame.math.Vector2(
    settings.display.matrix.width, settings.display.matrix.height
)


def setup_led_matrix() -> tuple[RGBMatrix, Any]:
    matrix = RGBMatrix(options=matrix_options)
    buffer = matrix.CreateFrameCanvas()
    return matrix, buffer


def render_led_matrix(
    matrix: RGBMatrix,
    surface: pygame.surface.Surface,
    buffer: Any,
    brightness: int = None,
) -> Any:
    # pixels = pygame.surfarray.pixels3d(surface)
    pil_image = Image.fromarray(pygame.surfarray.array3d(surface))
    np_image = np.array(pil_image, dtype=np.uint8)
    wrapped = wrap_surface_nparray(np_image, MATRIX_SIZE)
    led_image = np.transpose(np_image, (1, 0, 2))

    # image = Image.fromarray(wrapped).convert("RGB")
    buffer.SetImage(led_image)
    if brightness is not None:
        matrix.brightness = brightness
    return matrix.SwapOnVSync(buffer)


def blank_surface(size: pygame.math.Vector2):
    surface = pygame.surface.Surface(size)
    surface.fill(0)
    return surface


def wrap_surface_nparray(array: Any, new_shape: pygame.math.Vector2) -> Any:
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


def wrap_surface_blit(
    surface: pygame.surface.Surface,
    new_shape: pygame.math.Vector2,
    tile_size: pygame.math.Vector2,
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
            pygame.rect.Rect(x, 0, x + wrapped_width, surface_height),
        )
        row += 1
    return temp_surface
