from pygame import Color, Font, Surface
from pygame.sprite import Sprite


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


def test_sprite(size=20) -> Sprite:
    return ColoredBlockSprite(Color("white"), size, size)


def clock_sprite(text: str, font_size: int = 80) -> Sprite:
    font = Font(None, font_size)
    font_surface = font.render(text, True, Color("white"))
    return SurfaceSprite(font_surface)


def hass_sprite(text: str, font_size: int = 40) -> Sprite:
    font = Font(None, font_size)
    font_surface = font.render(text, True, Color("yellow"))
    return SurfaceSprite(font_surface)
