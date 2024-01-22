from pygame import Color, Surface, SRCALPHA
from pygame.sprite import Sprite


def build_square_sprite(color: Color, size=12):
    return ColoredBlockSprite(color, size, size)


def build_rect_sprite(color: Color, width=12, height=12):
    return ColoredBlockSprite(color, width, height)


class ColoredBlockSprite(Sprite):
    def __init__(self, color: Color, width: int, height: int) -> None:
        Sprite.__init__(self)
        self.image = Surface((width, height), SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()


class SurfaceSprite(Sprite):
    def __init__(self, surface: Surface) -> None:
        Sprite.__init__(self)
        self.image = surface
        self.rect = self.image.get_rect()
