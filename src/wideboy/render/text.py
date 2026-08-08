from __future__ import annotations

import pygame


def render_text(
    text: str,
    font_filename: str,
    font_size: int,
    color_fg: pygame.Color = pygame.Color(255, 255, 255, 255),
    color_bg: pygame.Color = pygame.Color(0, 0, 0, 0),
    color_outline: pygame.Color | None = None,
    antialias: bool = True,
) -> pygame.Surface:
    font = pygame.font.Font(font_filename, font_size)
    surface_orig = font.render(text, antialias, color_fg).convert_alpha()
    padding = 2 if color_outline else 0
    surface_dest = pygame.Surface(
        (surface_orig.get_width() + padding, surface_orig.get_height() + padding),
        pygame.SRCALPHA,
    )
    surface_dest.fill(color_bg)
    if color_outline:
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_surf = font.render(text, antialias, color_outline).convert_alpha()
            surface_dest.blit(outline_surf, (dx + 1, dy + 1))
        surface_dest.blit(surface_orig, (1, 1))
    else:
        surface_dest.blit(surface_orig, (0, 0))
    surface_dest.set_alpha(color_fg.a)
    return surface_dest
