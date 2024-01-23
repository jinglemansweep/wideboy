import logging
from pygame import Color, Surface
from typing import Dict, List, Type
from ...sprites.image import ImageFileSprite, ImageSprite
from ...sprites.text import TextSprite
from ...sprites.tile_grid import TileGrid, TileGridCell

logger = logging.getLogger(__name__)


def build_image_sprite(surface: Surface):
    return ImageSprite(surface)


def build_image_file_sprite(
    filename: str, alpha: int = 255, flip_x=False, flip_y=False
):
    return ImageFileSprite(filename, alpha=alpha, flip_x=flip_x, flip_y=flip_y)


def build_system_message_sprite(text: str):
    color_fg = Color(255, 0, 0, 255)
    color_outline = Color(0, 0, 0, 255)
    return TextSprite(
        text, font_size=32, color_fg=color_fg, color_outline=color_outline
    )


def build_time_sprite(text: str, night: bool = False):
    color_fg = Color(255, 255, 0, 255) if not night else Color(0, 0, 0, 255)
    color_outline = Color(0, 0, 0, 255) if not night else Color(192, 0, 192, 255)
    return TextSprite(
        text, font_size=36, color_fg=color_fg, color_outline=color_outline
    )


def build_date_sprite(text: str, night: bool = False):
    color_fg = Color(255, 255, 255, 255) if not night else Color(0, 0, 0, 255)
    color_outline = Color(0, 0, 0, 255) if not night else Color(192, 0, 192, 255)
    return TextSprite(
        text,
        font_size=17,
        color_fg=color_fg,
        color_outline=color_outline,
    )


def build_tile_grid_sprite(
    cells: List[List[Type[TileGridCell]]], state: Dict
) -> TileGrid:
    return TileGrid(cells, state)
