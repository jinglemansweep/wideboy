import logging


from pygame import Color, Rect, Surface
from pygame.sprite import Sprite
from ..graphics import render_text


logger = logging.getLogger(__name__)

FONT_FILENAME = "fonts/white-rabbit.ttf"


def build_system_message_sprite(text: str):
    color_fg = Color(255, 255, 255, 255)
    color_outline = Color(0, 0, 0, 255)
    return TextSprite(
        text, font_size=14, color_fg=color_fg, color_outline=color_outline
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


class TextSprite(Sprite):
    image: Surface
    rect: Rect

    def __init__(
        self,
        text: str,
        font_name: str = FONT_FILENAME,
        font_size: int = 36,
        color_bg: Color = Color(0, 0, 0, 0),
        color_fg: Color = Color(255, 255, 255, 255),
        color_outline: Color = Color(0, 0, 0, 255),
    ) -> None:
        self.image = self.render(
            text, font_name, font_size, color_bg, color_fg, color_outline
        )
        self.rect = self.image.get_rect()

    def render(
        self,
        text: str,
        font_name: str,
        font_size: int,
        color_bg: Color,
        color_fg: Color,
        color_outline: Color,
    ) -> Surface:
        return render_text(
            text,
            font_name,
            font_size,
            color_bg=color_bg,
            color_fg=color_fg,
            color_outline=color_outline,
        )
