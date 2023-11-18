import glob
import pygame
from pygame import Color, Surface, Vector2, SRCALPHA
from typing import Optional


def render_text(
    text: str,
    font_filename: str,
    font_size: int,
    color_fg: Color,
    color_bg: Optional[Color] = None,
    color_outline: Optional[Color] = None,
    antialias: bool = True,
) -> pygame.surface.Surface:
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
    if color_bg is not None:
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
