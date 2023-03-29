import logging
import pygame

logger = logging.getLogger("sprites.base")


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self, rect: pygame.rect.Rect) -> None:
        super().__init__()
        self.rect = rect

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
