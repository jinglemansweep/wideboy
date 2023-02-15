import logging
import pygame
from pytweening import easeInOutSine
from typing import Optional

logger = logging.getLogger(__name__)


class Mover:
    def __init__(self, sprite, tweener=easeInOutSine):
        self.sprite: pygame.sprite.Sprite = sprite
        self.tweener = tweener
        self.target: Optional[tuple[int, int]] = None
        self.current: Optional[tuple[int, int]] = self.sprite.rect.x, self.sprite.rect.y
        self.origin: Optional[tuple[int, int]] = None
        self.length: Optional[int] = None
        self.index = None

    def move(self, target: tuple[int, int], length: int):
        self.origin = self.current
        self.target = target
        self.length = length
        self.distances = (
            (self.target[0] - self.origin[0]),
            (self.target[1] - self.origin[1]),
        )
        self.index = 0
        logger.debug(
            f"sprite::mover::move current={self.current} target={self.target} length={self.length} distances={self.distances}"
        )

    def is_moving(self):
        return self.index is not None and self.index < self.length

    def tick(self, update_sprite=True):
        if not self.is_moving():
            return
        ri = self.index / self.length
        tween_val = self.tweener(ri)
        x = self.origin[0] + (self.distances[0] * tween_val)
        y = self.origin[1] + (self.distances[1] * tween_val)
        self.current = (x, y)
        if update_sprite:
            self.sprite.rect.x, self.sprite.rect.y = self.current
            self.sprite.dirty = 1
        self.index += 1


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self, rect: pygame.rect.Rect):
        super().__init__()
        self.rect = pygame.rect.Rect(*rect)
        self.mover = Mover(self)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.mover:
            self.mover.tick()
