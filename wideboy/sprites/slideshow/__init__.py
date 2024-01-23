import logging
from pygame import Rect, Surface
from pygame.sprite import Sprite
from typing import Optional

logger = logging.getLogger(__name__)


class SlideshowSprite(Sprite):
    image: Surface
    image_buffer: Optional[Surface] = None
    rect: Rect

    def __init__(self, surface: Surface) -> None:
        self.image = surface
        self.rect = self.image.get_rect()

    def set_next_image(self, surface: Surface) -> None:
        self.image_buffer = surface

    def swap(self) -> None:
        if self.image_buffer is None:
            return
        self.image = self.image_buffer
        self.image_buffer = None
