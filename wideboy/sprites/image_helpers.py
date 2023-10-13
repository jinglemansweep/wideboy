import glob
import logging
import math
import os
import pygame
from PIL import Image, ImageFilter, ImageEnhance
from pygame import Color, Surface, Vector2, SRCALPHA
from typing import Optional

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger("sprites.image_helpers")


def load_image(filename: str, convert_alpha=False) -> Surface:
    image = pygame.image.load(filename)
    if convert_alpha:
        image = image.convert_alpha()
    return image


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
) -> pygame.surface.Surface:
    # logger.debug(f"render_text: text={text}")
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg).convert_alpha()
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
            surface_outline = font.render(
                text, antialias, color_outline
            ).convert_alpha()
            surface_dest.blit(surface_outline, (offset[0] + 1, offset[1] + 1))
        surface_dest.blit(surface_orig, (1, 1))
    else:
        surface_dest.blit(surface_orig, (0, 0))
    surface_dest.set_alpha(color_fg.a)
    return surface_dest


def render_arrow(
    start_pos: tuple[int, int] = (0, 0),
    length: int = 10,
    angle: int = 0,
    color: Color = Color(255, 255, 255, 255),
    adjust: int = 0,
):
    surface = pygame.Surface((length * 2, length * 2), pygame.SRCALPHA)
    rect = surface.get_rect()
    rect.center = start_pos
    angle = 360 - angle + 90 + adjust
    tip_pos = (
        length * math.cos(math.radians(angle)),
        -length * math.sin(math.radians(angle)),
    )
    base_angle1 = angle + 135
    base_angle2 = angle - 135
    base_point1 = (
        length + length * math.cos(math.radians(base_angle1)),
        length - length * math.sin(math.radians(base_angle1)),
    )
    base_point2 = (
        length + length * math.cos(math.radians(base_angle2)),
        length - length * math.sin(math.radians(base_angle2)),
    )
    pygame.draw.polygon(
        surface,
        color,
        [(length + tip_pos[0], length + tip_pos[1]), base_point1, base_point2],
    )
    return surface


def render_grid(
    size: tuple[int, int],
    spacing: int,
    color: Color,
    zoom: float,
    angle: float,
    line_size: int = 1,
) -> Surface:
    width, height = size
    surface = Surface((width, height))
    center_x, center_y = width // 2, height // 2
    radians = math.radians(angle)
    for x in range(-width, width, int(spacing * zoom)):
        for y in range(-height, height, int(spacing * zoom)):
            # Calculate the rotated endpoints for horizontal and vertical lines
            x1 = x * math.cos(radians) - y * math.sin(radians)
            y1 = x * math.sin(radians) + y * math.cos(radians)
            x2 = (x + int(spacing * zoom)) * math.cos(radians) - y * math.sin(radians)
            y2 = (x + int(spacing * zoom)) * math.sin(radians) + y * math.cos(radians)
            x3 = x * math.cos(radians) - (y + int(spacing * zoom)) * math.sin(radians)
            y3 = x * math.sin(radians) + (y + int(spacing * zoom)) * math.cos(radians)
            # Draw horizontal and vertical lines
            pygame.draw.line(
                surface,
                color,
                (center_x + x1, center_y - y1),
                (center_x + x2, center_y - y2),
                line_size,
            )
            pygame.draw.line(
                surface,
                color,
                (center_x + x1, center_y - y1),
                (center_x + x3, center_y - y3),
                line_size,
            )
    return surface


class MaterialIcons:
    MDI_DELETE = 0xE872
    MDI_DOWNLOAD = 0xE2C4
    MDI_UPLOAD = 0xE2C6
    MDI_NETWORK_PING = 0xEBCA
    MDI_WIFI = 0xE63E
    MDI_SYNC_ALT = 0xEA18
    MDI_VPN_LOCK = 0xE62F
    MDI_LOCK = 0xE897
    MDI_DNS = 0xE875
    MDI_AC_UNIT = 0xEB3B
    MDI_LIGHTBULB = 0xE0F0
    MDI_DOOR = 0xF1B5
    MDI_DIRECTIONS_WALK = 0xE536
    MDI_BOLT = 0xEA0B
    MDI_TOGGLE_ON = 0xE9F6
    MDI_CURRENCY_POUND = 0xEAF1
    MDI_CURRENCY_DOLLAR = 0xE227
    MDI_BATTERY = 0xE1A4
    MDI_SCHEDULE = 0xE8B5
    MDI_HOURGLASS = 0xE88C
    MDI_POWER = 0xE63C
    MDI_SYMBOL_AT = 0xE0E6
    MDI_CALENDAR_TODAY = 0xE935
    MDI_LIGHT_MODE = 0xE518
    MDI_SCHEDULE = 0xE8B5
    MDI_LOOP = 0xE028


def render_material_icon(
    codepoint: int,
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


def rainbow_color(step: float, alpha: int = 255):
    r = int(255 * (1 + math.sin(step)) / 2)
    g = int(255 * (1 + math.sin(step + (2 * math.pi / 3))) / 2)
    b = int(255 * (1 + math.sin(step + (4 * math.pi / 3))) / 2)
    return (r, g, b, alpha)


def build_background(size: Vector2, color: Color) -> Surface:
    background = Surface(size)
    background.fill(color)
    return background
