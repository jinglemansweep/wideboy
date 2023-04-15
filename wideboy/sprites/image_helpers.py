import glob
import logging
import os
import pygame
from PIL import Image, ImageFilter, ImageEnhance
from pygame import Color, Surface, Vector2, SRCALPHA
from typing import Optional

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger("sprites.image_helpers")


def load_image(filename: str) -> Surface:
    return pygame.image.load(filename).convert_alpha()


def pil_to_surface(image: Image.Image) -> Surface:
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode).convert_alpha()  # type: ignore


def surface_to_pil(surface: Surface) -> Image.Image:
    image_bytes = pygame.image.tostring(surface, "RGBA")
    return Image.frombytes(
        "RGBA", (surface.get_width(), surface.get_height()), image_bytes
    )


def scale_surface(surface: Surface, size: Vector2) -> Surface:
    return pygame.transform.smoothscale(surface, size)


def filter_surface(
    surface: Surface,
    alpha: int = 255,
    filters: Optional[list[ImageFilter.Filter]] = None,
) -> Surface:
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


def tile_surface(surface: Surface, size: Vector2) -> Surface:
    x = y = 0
    tiled_surface = Surface(size)
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
    color_fg: Color,
    color_bg: Color = Color(0, 0, 0, 0),
    color_outline: Optional[Color] = None,
    antialias: bool = True,
    alpha: int = 255,
) -> pygame.surface.Surface:
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg)
    padding = 2 if color_outline else 0
    surface_dest = pygame.Surface(
        (
            surface_orig.get_rect().width + padding,
            surface_orig.get_rect().height + padding,
        ),
        SRCALPHA,
    )
    surface_dest.fill(color_bg)
    if color_outline:
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            surface_outline = font.render(text, antialias, color_outline)
            surface_dest.blit(surface_outline, (offset[0] + 1, offset[1] + 1))
        surface_dest.blit(surface_orig, (1, 1))
    else:
        surface_dest.blit(surface_orig, (0, 0))
    return surface_dest


class MaterialIcons:
    MDI_DELETE = 0xE872
    MDI_DOWNLOAD = 0xE2C4
    MDI_UPLOAD = 0xE2C6
    MDI_WIFI = 0xE63E
    MDI_SYNC_ALT = 0xEA18
    MDI_VPN_LOCK = 0xE62F
    MDI_DNS = 0xE875


def render_material_icon(
    codepoint: str,
    size: int = 12,
    color_fg: Color = Color(255, 255, 255, 255),
    color_outline: Optional[Color] = None,
) -> Surface:
    icon_char = chr(codepoint)
    icon = render_text(
        icon_char,
        "fonts/material-icons.ttf",
        size,
        color_fg=color_fg,
        color_outline=color_outline,
    )
    surface = Surface((icon.get_rect().width, icon.get_rect().height), SRCALPHA)
    surface.blit(icon, (0, 0))
    return surface


def build_background(size: Vector2, color: Color) -> Surface:
    background = Surface(size)
    background.fill(color)
    return background
