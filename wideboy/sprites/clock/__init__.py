import logging

from datetime import datetime
from pygame import Color, Rect, Surface, SRCALPHA
from pygame.sprite import Sprite
from ..graphics import render_text


logger = logging.getLogger(__name__)

FONT_FILENAME = "fonts/white-rabbit.ttf"
CLOCK_WIDTH = 105


def time_to_color(hour: int) -> Color:
    if hour > 6 and hour < 18:
        return Color(255, 255, 0, 255)
    else:
        return Color(255, 128, 192, 255)


class TimeSprite(Sprite):
    image: Surface
    rect: Rect = Rect(0, 0, CLOCK_WIDTH, 30)
    font_name: str = FONT_FILENAME
    font_size: int = 36
    text_align: str = "center"
    color_bg: Color = Color(0, 0, 0, 0)
    color_fg: Color = Color(255, 0, 255, 255)
    color_outline: Color = Color(0, 0, 0, 255)
    pos_adj: tuple[int, int] = (0, 0)

    def __init__(
        self,
        now: datetime,
        hours_24: bool,
    ) -> None:
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.now = now
        self.hours_24 = hours_24
        self.render(now)

    def render_text_surface(self) -> Surface:
        time_str = self.now.strftime("%H:%M" if self.hours_24 else "%I:%M")
        return render_text(
            time_str,
            self.font_name,
            self.font_size,
            color_bg=self.color_bg,
            color_fg=time_to_color(self.now.hour),
            color_outline=self.color_outline,
        )

    def render(self, now: datetime) -> None:
        self.image.fill(self.color_bg)
        surface = self.render_text_surface()
        x: float = (self.rect.width / 2) - (surface.get_rect().width / 2)
        if self.text_align == "left":
            x = 0.0
        elif self.text_align == "right":
            x = self.rect.width - surface.get_rect().width
        self.image.blit(
            surface,
            (
                x + self.pos_adj[0],
                0 + self.pos_adj[1],
            ),
        )


def build_clock_time_sprite(now: datetime, hours_24: bool):
    return TimeSprite(now, hours_24=hours_24)


class DateSprite(Sprite):
    image: Surface
    rect: Rect = Rect(0, 0, CLOCK_WIDTH, 16)

    def __init__(
        self,
        now: datetime,
        color_bg: Color = Color(0, 0, 0, 0),
        color_fg: Color = Color(192, 192, 255, 255),
        color_outline: Color = Color(0, 0, 0, 255),
        font_name: str = FONT_FILENAME,
        font_size: int = 16,
        date_format: str = "%a %d %b",
        uppercase: bool = True,
        align: str = "center",
        pos_adj: tuple[int, int] = (0, 0),
    ) -> None:
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.now = now
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.font_name = font_name
        self.font_size = font_size
        self.date_format = date_format
        self.uppercase = uppercase
        self.align = align
        self.pos_adj = pos_adj
        self.dirty = 1
        self.render_text_surface()
        self.render()

    def render_text_surface(self) -> None:
        date_str = self.now.strftime(self.date_format)
        if self.uppercase:
            date_str = date_str.upper()
        self.surface_text = render_text(
            date_str,
            self.font_name,
            self.font_size,
            color_bg=self.color_bg,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )

    def render(self) -> None:
        self.image.fill(self.color_bg)
        x: float = (self.rect.width / 2) - (self.surface_text.get_rect().width / 2)
        if self.align == "left":
            x = 0.0
        elif self.align == "right":
            x = self.rect.width - self.surface_text.get_rect().width
        self.image.blit(
            self.surface_text,
            (
                x,
                0 + self.pos_adj[1],
            ),
        )


def build_clock_date_sprite(now: datetime):
    return DateSprite(now)
