import logging
import pygame
from PIL import Image, ImageFilter, ImageEnhance
from pygame import Color, Surface, Vector2, BLEND_RGBA_MULT, SRCALPHA
from typing import Optional, Tuple

logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)
logger = logging.getLogger(__name__)


def load_image(filename: str, convert_alpha: bool = True) -> Surface:
    image = pygame.image.load(filename)
    if convert_alpha:
        image = image.convert_alpha()
    return image


def load_gif(filename: str, convert_alpha: bool = True) -> list[Surface]:
    gif_image = Image.open(filename)
    frames = []
    try:
        while True:
            gif_image.seek(gif_image.tell() + 1)
            gif_frame = gif_image.copy()
            if gif_frame:
                frame = pil_to_surface(gif_frame, convert_alpha)
                frames.append(frame)
    except EOFError:
        pass
    return frames


def pil_to_surface(image: Image.Image, convert_alpha: bool = True) -> Surface:
    if image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGBA")
    surface = pygame.image.fromstring(image.tobytes(), image.size, "RGBA")
    if convert_alpha:
        surface = surface.convert_alpha()  # type: ignore
    return surface


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


def recolor_image(image: Surface, color: Color) -> Surface:
    surface = Surface(image.get_size(), SRCALPHA)
    surface.fill(color)
    surface.blit(image, (0, 0), special_flags=BLEND_RGBA_MULT)
    return surface


def render_text(
    text: str,
    font_filename: str,
    font_size: int,
    color_fg: Color,
    color_bg: Color = Color(0, 0, 0, 0),
    color_outline: Optional[Color] = None,
    antialias: bool = True,
) -> pygame.Surface:
    # logger.debug(f"render_text: text={text}")
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg).convert_alpha()
    padding = 2 if color_outline else 0
    surface_dest = Surface(
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
    MDI_HOME = 0xE88A
    MDI_SOFA = 0xE16B
    MDI_BED = 0xE53A
    MDI_KITCHEN = 0xEB47


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


def build_surface(size: Tuple[int, int], color: Color) -> Surface:
    surface = Surface(size, SRCALPHA)
    surface.fill(color)
    return surface
