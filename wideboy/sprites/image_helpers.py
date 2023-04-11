import glob
import logging
import os
import pygame
from PIL import Image, ImageFilter, ImageEnhance
from pygame import SRCALPHA
from typing import Optional

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger("sprites.image_helpers")


def load_image(filename: str) -> pygame.surface.Surface:
    return pygame.image.load(filename).convert_alpha()


def pil_to_surface(image: Image.Image) -> pygame.surface.Surface:
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()  # type: ignore


def surface_to_pil(surface: pygame.surface.Surface) -> Image.Image:
    image_bytes = pygame.image.tostring(surface, "RGBA")
    return Image.frombytes(
        "RGBA", (surface.get_width(), surface.get_height()), image_bytes
    )


def scale_surface(
    surface: pygame.surface.Surface, size: pygame.math.Vector2
) -> pygame.surface.Surface:
    return pygame.transform.smoothscale(surface, size)


def filter_surface(
    surface: pygame.surface.Surface,
    alpha: int = 255,
    filters: Optional[list[ImageFilter.Filter]] = None,
) -> pygame.surface.Surface:
    image = surface_to_pil(surface)
    if filters is None:
        filters = []
    for filter in filters:
        image = image.filter(filter)
    brightness_ctrl = ImageEnhance.Brightness(image)
    image = brightness_ctrl.enhance(alpha / 255)
    return pil_to_surface(image)


def glob_files(path: str = ".", pattern: str = "*.*") -> list[str]:
    return glob.glob(os.path.join(path, pattern))


def tile_surface(
    surface: pygame.Surface, size: pygame.math.Vector2
) -> pygame.surface.Surface:
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
    color_bg: pygame.color.Color = pygame.color.Color(0, 0, 0, 0),
    color_outline: pygame.color.Color = pygame.color.Color(0, 0, 0, 255),
    antialias: bool = True,
    alpha: int = 255,
) -> pygame.surface.Surface:
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg)
    surface_dest = pygame.Surface(
        (surface_orig.get_rect().width + 4, surface_orig.get_rect().height + 2),
        SRCALPHA,
    )
    surface_dest.fill(color_bg)
    for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        surface_outline = font.render(text, antialias, color_outline)
        surface_dest.blit(surface_outline, (offset[0] + 2, offset[1] + 1))
    surface_dest.blit(surface_orig, (2, 1))
    surface_dest.set_alpha(alpha)
    return surface_dest


def build_background(
    size: pygame.math.Vector2, color: pygame.color.Color
) -> pygame.surface.Surface:
    background = pygame.surface.Surface(size)
    background.fill(color)
    return background
