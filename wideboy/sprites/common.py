from pygame import Color, Font, Surface
from pygame.sprite import Sprite


class ColoredBlockSprite(Sprite):
    def __init__(self, color: Color, width: int, height: int) -> None:
        Sprite.__init__(self)
        self.image = Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()


class SurfaceSprite(Sprite):
    def __init__(self, surface: Surface) -> None:
        Sprite.__init__(self)
        self.image = surface
        self.rect = self.image.get_rect()


def clock_sprite(text: str, font_size: int = 80) -> Sprite:
    font = Font(None, font_size)
    font_surface = font.render(text, True, Color("white"))
    return SurfaceSprite(font_surface)


def test_sprite(color: Color, size=20) -> Sprite:
    return ColoredBlockSprite(color, size, size)
