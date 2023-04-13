import logging
from pygame import Rect
from pygame.sprite import DirtySprite

logger = logging.getLogger("sprites.base")


class BaseSprite(DirtySprite):
    def __init__(self, rect: Rect) -> None:
        super().__init__()
        self.rect = rect

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
