import pygame
from typing import Any
from PIL import Image
from rgbmatrix import RGBMatrix  # type: ignore

from wideboy.config import matrix_options


def setup_led_matrix():
    matrix = RGBMatrix(options=matrix_options)
    buffer = matrix.CreateFrameCanvas()
    return matrix, buffer


def render_led_matrix(matrix: RGBMatrix, surface: pygame.surface.Surface, buffer: Any):
    temp_surface = pygame.surface.Surface((256,192))
    # Blit first 4 panels to top row
    temp_surface.blit(
        surface,
        (0, 0),
        (0, 0, 64 * 4, 64 * 1),
    )
    # Blit next 4 panels to next row
    temp_surface.blit(
        surface,
        (0, 64 * 1),
        (64 * 4, 0, (64 * 4), 64 * 1),
    )
    # Convert PyGame surface to RGB byte array
    image_str = pygame.image.tostring(temp_surface, "RGB", False)
    # Create a PIL compatible image from the byte array
    image_rgb = Image.frombytes("RGB", (64 * 4, 64 * 3), image_str).convert()
    # Render PIL image to buffer
    buffer.SetImage(image_rgb)
    # Flip and return next buffer
    return matrix.SwapOnVSync(buffer)
