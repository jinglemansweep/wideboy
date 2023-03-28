import glob
import logging
import os
import pygame
from PIL import Image, ImageFilter
from pygame import SRCALPHA
from typing import Optional

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger("sprites.utils.images")


def load_image(filename: str) -> Image.Image:
    return Image.open(filename)


def pil_to_surface(image: Image.Image) -> pygame.surface.Surface:
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()  # type: ignore


def surface_to_pil(surface: pygame.surface.Surface) -> Image.Image:
    image_bytes = pygame.image.tostring(surface, "RGBA")
    return Image.frombytes(
        "RGBA", (surface.get_width(), surface.get_height()), image_bytes
    )


def load_transform_image(
    filename: str, size: Optional[pygame.math.Vector2] = None, blur: bool = False
) -> pygame.surface.Surface:
    im = load_image(filename)
    if size is not None:
        im.thumbnail((int(size[0]), int(size[1])), Image.Resampling.LANCZOS)
    surface = pil_to_surface(im)
    return surface


def apply_surface_filter(surface: pygame.surface.Surface, filter: ImageFilter.Filter):
    image = surface_to_pil(surface)
    image = image.filter(filter)
    return pil_to_surface(image)


def glob_files(path: str = ".", pattern: str = "*.*") -> list[str]:
    return glob.glob(os.path.join(path, pattern))


def tile_surface(surface: pygame.Surface, size: pygame.math.Vector2) -> pygame.Surface:
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
    font_filename: str,
    font_size: int,
    color_fg: pygame.color.Color,
    color_outline: pygame.color.Color = pygame.color.Color(0, 0, 0, 255),
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
