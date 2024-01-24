import logging
from pygame import Rect, Surface
from pygame.sprite import Sprite


logger = logging.getLogger(__name__)


class ImageSprite(Sprite):
    image: Surface
    rect: Rect

    def __init__(self, surface: Surface) -> None:
        self.image = surface
        self.image_orig = self.image.copy()
        self.rect = self.image.get_rect()
