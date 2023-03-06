import glob
import logging
import os
import pygame
from PIL import Image
from pygame import SRCALPHA
from typing import Optional

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger("sprites.utils.images")


def load_image(filename: str) -> Image.Image:
    return Image.open(filename)


def load_resize_image(
    filename: str, size: Optional[tuple[int, int]] = None
) -> pygame.surface.Surface:
    im = load_image(filename)
    if size is not None:
        im.thumbnail(size, Image.Resampling.LANCZOS)
    image = pygame.image.fromstring(im.tobytes(), im.size, im.mode).convert_alpha()  # type: ignore
    return image


def glob_files(path: str = ".", pattern: str = "*.*") -> list[str]:
    return glob.glob(os.path.join(path, pattern))


def tile_surface(surface: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    x = y = 0
    tiled_surface = pygame.Surface(size)
    while y < size[1]:
        while x < size[0]:
            tiled_surface.blit(surface, (x, y))
            x += surface.get_width()
        y += surface.get_height()
        x = 0
    return tiled_surface


def render_text(
    text: str,
    font_filename: pygame.font.Font,
    font_size: int,
    color_fg: pygame.color.Color,
    color_outline: pygame.color.Color = (0, 0, 0, 255),
    antialias: bool = True,
) -> pygame.surface.Surface:
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg)
    surface_dest = pygame.Surface(
        (surface_orig.get_rect().width + 2, surface_orig.get_rect().height + 2),
        SRCALPHA,
    )
    for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        surface_outline = font.render(text, antialias, color_outline)
        surface_dest.blit(surface_outline, (offset[0] + 1, offset[1] + 1))
    surface_dest.blit(surface_orig, (1, 1))
    return surface_dest
