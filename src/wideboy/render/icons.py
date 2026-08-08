from __future__ import annotations

import pygame

ICON_FONT_FILENAME = "fonts/fontawesome-solid.otf"
ICON_FONT_SIZE = 9


def render_icon(
    width: int,
    height: int,
    codepoint: int,
    color_background: pygame.Color,
    color_foreground: pygame.Color,
    color_outline: pygame.Color | None = None,
    font_filename: str = ICON_FONT_FILENAME,
    font_size: int = ICON_FONT_SIZE,
) -> pygame.Surface:
    from .text import render_text

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(color_background)
    if codepoint is not None:
        label_surface = render_text(
            text=chr(codepoint),
            font_filename=font_filename,
            font_size=font_size,
            color_fg=color_foreground,
            color_outline=color_outline,
        )
        x = (width - label_surface.get_width()) // 2
        y = (height - label_surface.get_height()) // 2
        surface.blit(label_surface, (x, y))
    return surface
