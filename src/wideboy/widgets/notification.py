from __future__ import annotations

import time
from typing import Any

import pygame

from ..render.text import render_text
from .base import Widget

_DEFAULTS = {
    "font": "fonts/white-rabbit.ttf",
    "font_size": 14,
    "color_fg": [255, 255, 255, 255],
    "color_outline": [0, 0, 0, 255],
    "color_bar": [0, 0, 0, 180],
    "duration": 30.0,
    "scroll_speed": 60.0,
    "bar_height": 18,
    "right_margin": 128,
    "fade_duration": 1.0,
}


class NotificationOverlay(Widget):
    def __init__(
        self,
        state: Any,
        canvas_width: int = 768,
        canvas_height: int = 64,
        position: tuple[int, int] = (0, 0),
        z_order: int = 50,
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(position=position, z_order=z_order, settings=settings)
        self._state = state
        self._canvas_w = canvas_width
        self._canvas_h = canvas_height
        self._merged = {**_DEFAULTS, **(settings or {})}
        self._text_surface: pygame.Surface | None = None
        self._current_text: str | None = None
        self._elapsed: float = 0.0
        self._fade_alpha: int = 255
        self.visible = False

    def _build_text_surface(self, text: str) -> pygame.Surface:
        s = self._merged
        return render_text(
            text,
            s["font"],
            s["font_size"],
            color_fg=pygame.Color(*s["color_fg"]),
            color_outline=pygame.Color(*s["color_outline"]),
        )

    def update(self, dt: float) -> None:
        notification = self._state.notification
        if notification is None:
            self.visible = False
            return

        now = time.monotonic()
        if now >= notification["expire_time"]:
            self._state.notification = None
            self._current_text = None
            self._text_surface = None
            self.visible = False
            return

        self.visible = True
        text = notification["text"]

        if text != self._current_text:
            self._current_text = text
            self._text_surface = self._build_text_surface(text)

        self._elapsed = now - notification["received_at"]

        remaining = notification["expire_time"] - now
        fade_dur = self._merged["fade_duration"]
        if remaining < fade_dur:
            self._fade_alpha = max(0, int(255 * remaining / fade_dur))
        else:
            self._fade_alpha = 255

        self.mark_dirty()

    def _surface_size(self) -> tuple[int, int] | None:
        return (self._canvas_w, self._canvas_h)

    def _render(self, surface: pygame.Surface) -> None:
        if self._text_surface is None:
            return

        s = self._merged
        h = self._canvas_h
        bar_h = s["bar_height"]
        bar_w = self._canvas_w - s["right_margin"]
        bar_y = h - bar_h

        bar = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        bar.fill(tuple(s["color_bar"]))
        bar.set_alpha(self._fade_alpha)
        surface.blit(bar, (0, bar_y))

        text_surf = self._text_surface
        text_w = text_surf.get_width()
        text_y = bar_y + (bar_h - text_surf.get_height()) // 2

        scroll_speed = s["scroll_speed"]
        gap = 120
        period = bar_w + text_w + gap
        offset = int(self._elapsed * scroll_speed) % period
        x = bar_w - offset

        text_surf.set_alpha(self._fade_alpha)
        surface.set_clip(pygame.Rect(0, bar_y, bar_w, bar_h))
        surface.blit(text_surf, (x, text_y))
        if text_w >= bar_w and x + text_w < bar_w:
            surface.blit(text_surf, (x + text_w, text_y))
        surface.set_clip(None)

    @property
    def content_size(self) -> tuple[int, int]:
        return (self._canvas_w, self._canvas_h)
