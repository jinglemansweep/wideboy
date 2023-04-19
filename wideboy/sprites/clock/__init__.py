import logging

from datetime import datetime
from typing import Optional
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from wideboy.sprites.image_helpers import render_text, rainbow_color
from wideboy.constants import EVENT_EPOCH_SECOND
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.clock")


class TimeSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        color_bg: Color = (0, 0, 0, 0),
        color_fg: Color = (255, 0, 255, 255),
        color_outline: Color = (0, 0, 0, 255),
        font_name: str = "fonts/molot.otf",
        font_size: int = 36,
        time_format: str = "%H:%M",
        pos_adj: tuple[int, int] = (0, 0),
        rainbow: Optional[str] = None,
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.font_name = font_name
        self.font_size = font_size
        self.time_format = time_format
        self.pos_adj = pos_adj
        self.rainbow = rainbow
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        if self.rainbow == "fg":
            self.color_fg = rainbow_color(frame / 100)
        elif self.rainbow == "outline":
            self.color_outline = rainbow_color(frame / 100)
        self.render()

    def render(self) -> None:
        now = datetime.now()
        self.image.fill(self.color_bg)
        time_str = now.strftime(self.time_format)
        time_surface = render_text(
            time_str,
            self.font_name,
            self.font_size,
            color_bg=self.color_bg,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(
            time_surface,
            (
                (self.rect.width / 2)
                - (time_surface.get_rect().width / 2)
                + self.pos_adj[0],
                0 + self.pos_adj[1],
            ),
        )
        self.dirty = 1


class DateSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        color_bg: Color = (0, 0, 0, 0),
        color_fg: Color = (192, 192, 255, 255),
        color_outline: Color = (0, 0, 0, 255),
        font_name: str = "fonts/molot.otf",
        font_size: int = 16,
        date_format: str = "%a %d %b",
        uppercase: bool = True,
        pos_adj: tuple[int, int] = (0, 0),
        rainbow: Optional[str] = None,
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.font_name = font_name
        self.font_size = font_size
        self.date_format = date_format
        self.uppercase = uppercase
        self.pos_adj = pos_adj
        self.rainbow = rainbow
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        if self.rainbow == "fg":
            self.color_fg = rainbow_color(frame / 100)
        elif self.rainbow == "outline":
            self.color_outline = rainbow_color(frame / 100)
        self.render()

    def render(self) -> None:
        now = datetime.now()
        date_str = now.strftime(self.date_format)
        if self.uppercase:
            date_str = date_str.upper()
        self.image.fill(self.color_bg)
        date_surface = render_text(
            date_str,
            self.font_name,
            self.font_size,
            color_bg=self.color_bg,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(
            date_surface,
            (
                ((self.rect.width / 2) - date_surface.get_rect().width / 2)
                + self.pos_adj[0],
                0 + self.pos_adj[1],
            ),
        )
        self.dirty = 1
