import pygame
from typing import Tuple


# CONSTANTS

ICON_FONT_FILENAME = "fonts/fontawesome-solid.otf"
ICON_FONT_SIZE = 9

LABEL_FONT_FILENAME = "fonts/bitstream-vera.ttf"
LABEL_FONT_SIZE = 11

NOT_APPLICABLE = "N/A"

# CUSTOM COLORS


class CommonColors:
    COLOR_RED_DARK = pygame.Color(64, 0, 0, 255)
    COLOR_RED = pygame.Color(255, 0, 0, 255)
    COLOR_BLUE_DARK = pygame.Color(0, 0, 64, 255)
    COLOR_BLUE = pygame.Color(0, 0, 255, 255)
    COLOR_GREEN_DARK = pygame.Color(0, 64, 0, 255)
    COLOR_GREEN = pygame.Color(0, 196, 0, 255)
    COLOR_YELLOW_DARK = pygame.Color(64, 64, 0, 255)
    COLOR_YELLOW = pygame.Color(255, 255, 0, 255)
    COLOR_ORANGE_DARK = pygame.Color(64, 32, 0, 255)
    COLOR_ORANGE = pygame.Color(255, 128, 0, 255)
    COLOR_PURPLE_DARK = pygame.Color(64, 0, 64, 255)
    COLOR_PURPLE = pygame.Color(255, 0, 255, 255)
    COLOR_PINK_DARK = pygame.Color(64, 0, 32, 255)
    COLOR_PINK = pygame.Color(255, 0, 128, 255)
    COLOR_CYAN_DARK = pygame.Color(0, 64, 64, 255)
    COLOR_CYAN = pygame.Color(0, 255, 255, 255)
    COLOR_WHITE = pygame.Color(255, 255, 255, 255)
    COLOR_BLACK = pygame.Color(0, 0, 0, 255)
    COLOR_GREY = pygame.Color(64, 64, 64, 255)
    COLOR_GREY_DARK = pygame.Color(16, 16, 16, 255)
    COLOR_TRANSPARENT = pygame.Color(0, 0, 0, 0)


# FONTAWESOME CODEPOINTS


class FontAwesomeIcons:
    ICON_FA_POWER_OFF = 0xF011
    ICON_FA_BOLT = 0xF0E7
    ICON_FA_BATTERY_FULL = 0xF240
    ICON_FA_BATTERY_THREE_QUARTERS = 0xF241
    ICON_FA_BATTERY_HALF = 0xF242
    ICON_FA_BATTERY_QUARTER = 0xF243
    ICON_FA_BATTERY_EMPTY = 0xF244
    ICON_FA_HOURGLASS = 0xF254
    ICON_FA_HOURGLASS_HALF = 0xF252
    ICON_FA_CLOCK = 0xF017
    ICON_FA_PLUG_CIRCLE_PLUS = 0xE55F
    ICON_FA_PLUG_CIRCLE_MINUS = 0xE55E
    ICON_FA_CIRCLE_ARROW_DOWN = 0xF0AB
    ICON_FA_CIRCLE_ARROW_UP = 0xF0AA
    ICON_FA_HEART_PULSE = 0xF21E
    ICON_FA_HARD_DRIVE = 0xF0A0
    ICON_FA_FAN = 0xF863
    ICON_FA_HOUSE = 0xF015
    ICON_FA_COUCH = 0xF4B8
    ICON_FA_SINK = 0xE06D
    ICON_FA_BED = 0xF236
    ICON_FA_DICE_THREE = 0xF527
    ICON_FA_WIND = 0xF72E
    ICON_FA_PERSON_WALKING = 0xF554
    ICON_FA_DOOR_CLOSED = 0xF52A
    ICON_FA_TOGGLE_OFF = 0xF204
    ICON_FA_TOGGLE_ON = 0xF205
    ICON_FA_THERMOSTAT_EMPTY = 0xF2CB
    ICON_FA_SMOKING = 0xF48D
    ICON_FA_UMBRELLA = 0xF0E9
    ICON_FA_TREE = 0xF1BB
    ICON_FA_WAREHOUSE = 0xF494
    ICON_FA_ROAD = 0xF018
    ICON_FA_LEAF = 0xF06C
    ICON_FA_CIRCLE_HALF_STROKE = 0xF042
    ICON_FA_CALENDAR = 0xF133
    ICON_FA_PLUG = 0xF1E6
    ICON_FA_FIRE_FLAME_SIMPLE = 0xF46A
    ICON_FA_CAR_TUNNEL = 0xE4DE
    ICON_FA_CAR = 0xF1B9
    ICON_FA_CAMERA = 0xF030
    ICON_FA_TRASH_CAN = 0xF2ED
    ICON_FA_SHIELD_HALVED = 0xF3ED
    ICON_FA_BUG = 0xF188
    ICON_FA_WORM = 0xE599
    ICON_FA_CHEVRON_UP = 0xF077
    ICON_FA_CHEVRON_DOWN = 0xF078


# HELPER FUNCTIONS


def is_defined(value) -> bool:
    return value is not None and value not in ["unavailable", "unknown"]


def template_if_defined(value, template):
    return template.format(value) if is_defined(value) else NOT_APPLICABLE


def render_icon(
    width: int,
    height: int,
    codepoint: int,
    color_background: pygame.Color,
    color_foreground: pygame.Color,
    font_filename: str = ICON_FONT_FILENAME,
    font_size: int = ICON_FONT_SIZE,
) -> pygame.surface.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(color_background)
    if codepoint is not None:
        label_surface = render_text(
            text=chr(codepoint),
            font_filename=ICON_FONT_FILENAME,
            font_size=ICON_FONT_SIZE,
            color_foreground=color_foreground,
            padding=(0, 3),
        )
        surface.blit(label_surface, ((width // 2 - label_surface.get_width() // 2), 0))
    return surface


def render_text(
    text: str,
    font_filename: str = LABEL_FONT_FILENAME,
    font_size: int = LABEL_FONT_SIZE,
    antialias: bool = True,
    color_foreground: pygame.Color = pygame.Color(255, 255, 255, 255),
    color_outline: pygame.Color = pygame.Color(0, 0, 0, 0),
    color_background: pygame.Color = pygame.Color(0, 0, 0, 0),
    padding: Tuple[int, int] = (0, 0),
    outline: bool = True,
    alpha: int = 255,
) -> pygame.surface.Surface:
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_foreground)
    padding_outline = 2 if outline else 0
    surface_dest = pygame.Surface(
        (
            surface_orig.get_rect().width + padding[0] + padding_outline,
            surface_orig.get_rect().height + padding[1] + padding_outline,
        ),
        pygame.SRCALPHA,
    )
    if color_background is not None:
        surface_dest.fill(color_background)
    text_padding_adj = (padding[0], padding[1] - 3)
    if outline:
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            surface_outline = font.render(text, antialias, color_outline)
            surface_dest.blit(
                surface_outline,
                (
                    text_padding_adj[0] + offset[0] + 1,
                    text_padding_adj[1] + offset[1] + 1,
                ),
            )
        surface_dest.blit(
            surface_orig, (text_padding_adj[0] + 1, text_padding_adj[1] + 1)
        )
    else:
        surface_dest.blit(surface_orig, text_padding_adj)
    surface_dest.set_alpha(alpha)
    return surface_dest
