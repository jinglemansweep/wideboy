import logging
import pygame
from wideboy.utils.state import StateStore

logger = logging.getLogger(__name__)


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self, rect: pygame.rect.Rect, state: StateStore) -> None:
        super().__init__()
        self.rect = pygame.rect.Rect(*rect)
        self.state = state

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
