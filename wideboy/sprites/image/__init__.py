import logging
from pygame import Rect, Surface
from pygame.image import load as pygame_image_load
from pygame.transform import flip as pygame_transform_flip
from pygame.sprite import Sprite


logger = logging.getLogger(__name__)


class ImageSprite(Sprite):
    image: Surface
    rect: Rect

    def __init__(self, surface: Surface) -> None:
        self.image = surface
        self.rect = self.image.get_rect()


class ImageFileSprite(ImageSprite):
    filename: str
    image: Surface
    rect: Rect

    def __init__(
        self, filename: str, alpha: int = 255, flip_x=False, flip_y=False
    ) -> None:
        self.image = pygame_image_load(filename, "RGBA")
        if flip_x or flip_y:
            self.image = pygame_transform_flip(self.image, flip_x=flip_x, flip_y=flip_y)
        super().__init__(self.image)
