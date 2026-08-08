from __future__ import annotations

from datetime import datetime
from typing import Any

import pygame

from ..render.text import render_text
from .base import Widget

_DEFAULTS = {
    "time_format": "%H:%M",
    "date_format": "%a %d %b",
    "font_time": "fonts/white-rabbit.ttf",
    "font_date": "fonts/white-rabbit.ttf",
    "size_time": 44,
    "size_date": 17,
    "color_time": [255, 255, 0, 255],
    "color_date": [255, 255, 255, 255],
    "color_bar": [255, 255, 0, 80],
    "color_bar_tick": [255, 255, 0, 160],
    "color_outline": [0, 0, 0, 255],
    "width": 128,
    "height": 64,
}


class ClockWidget(Widget):
    def __init__(
        self,
        position: tuple[int, int] = (0, 0),
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(position=position, settings=settings)
        self._last_second = -1
        self._merged = {**_DEFAULTS, **(settings or {})}

    def update(self, dt: float) -> None:
        now = datetime.now()
        if now.second != self._last_second:
            self._last_second = now.second
            self.mark_dirty()

    def _render(self, surface: pygame.Surface) -> None:
        s = self._merged
        now = datetime.now()
        w = s["width"]

        time_text = now.strftime(s["time_format"])
        date_text = now.strftime(s["date_format"])

        color_outline = pygame.Color(*s["color_outline"])

        time_surface = render_text(
            time_text,
            s["font_time"],
            s["size_time"],
            color_fg=pygame.Color(*s["color_time"]),
            color_outline=color_outline,
        )
        date_surface = render_text(
            date_text,
            s["font_date"],
            s["size_date"],
            color_fg=pygame.Color(*s["color_date"]),
            color_outline=color_outline,
        )

        time_x = (w - time_surface.get_width()) // 2
        date_x = (w - date_surface.get_width()) // 2

        gap = 6
        total_h = time_surface.get_height() + gap + date_surface.get_height()
        h = s["height"]
        time_y = (h - total_h) // 2
        date_y = time_y + time_surface.get_height() + gap

        surface.blit(time_surface, (time_x, time_y))

        content_w = max(time_surface.get_width(), date_surface.get_width())
        content_x = (w - content_w) // 2
        progress = now.second / 60.0
        bar_w = int(content_w * progress)
        bar_y = time_y + time_surface.get_height() + 1

        if bar_w > 0:
            bar_surf = pygame.Surface((bar_w, 2), pygame.SRCALPHA)
            bar_surf.fill(pygame.Color(*s["color_bar"]))
            surface.blit(bar_surf, (content_x, bar_y))

        color_bar_tick = pygame.Color(*s["color_bar_tick"])
        color_bar_dim = pygame.Color(*s["color_bar"])
        for tick_sec in (9, 19, 29, 39, 49, 59):
            tick_x = content_x + int(content_w * tick_sec / 60)
            color = color_bar_tick if now.second >= tick_sec else color_bar_dim
            surface.fill(color, pygame.Rect(tick_x, bar_y, 1, 2))

        surface.blit(date_surface, (date_x, date_y))

    @property
    def content_size(self) -> tuple[int, int]:
        s = self._merged
        return (s["width"], s["height"])
