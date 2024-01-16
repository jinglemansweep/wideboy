from pygame import Color, Font, Surface
from pygame.sprite import Sprite
from typing import Dict, List

from ...sprites.tile_grid_ecs import TileGrid


class ColoredBlockSprite(Sprite):
    def __init__(self, color: Color, width: int, height: int):
        Sprite.__init__(self)
        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()


class SurfaceSprite(Sprite):
    def __init__(self, surface: Surface):
        Sprite.__init__(self)
        self.image = surface
        self.rect = self.image.get_rect()


def clock_sprite(text: str, font_size: int = 80) -> Sprite:
    font = Font(None, font_size)
    font_surface = font.render(text, True, Color("white"))
    return SurfaceSprite(font_surface)


def test_sprite(size=20) -> Sprite:
    return ColoredBlockSprite(Color("white"), size, size)


def tilegrid_sprite(cells: List, state: Dict) -> Sprite:
    return TileGrid(cells, state)
