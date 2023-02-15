import logging
import pygame
from pytweening import easeInOutSine
from typing import Optional

logger = logging.getLogger(__name__)


class Mover:
    def __init__(self, tweener=easeInOutSine):
        self.tweener = tweener
        self.start: Optional[tuple[int, int]] = None
        self.target: Optional[tuple[int, int]] = None
        self.current: Optional[tuple[int, int]] = None
        self.length: Optional[int] = None
        self.index = None

    def move(self, start: tuple[int, int], target: tuple[int, int], length: int):
        self.start = self.current = start
        self.target = target
        self.length = length
        self.distances = (
            (self.target[0] - self.start[0]),
            (self.target[1] - self.start[1]),
        )
        self.steps = (self.distances[0] / length, self.distances[1] / length)
        self.index = 0
        print(
            f"Mover::move start={self.start} target={self.target} length={self.length} distances={self.distances} steps={self.steps}"
        )

    def is_moving(self):
        return self.index is not None and self.index < self.length

    def tick(self):
        if not self.is_moving():
            return
        ri = self.index / self.length
        tween_val = self.tweener(ri)
        x = self.start[0] + (self.distances[0] * tween_val)
        y = self.start[1] + (self.distances[1] * tween_val)
        self.current = (x, y)
        self.index += 1


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self):
        super().__init__()
        logger.debug(f"BaseSprite")
        self.mover = Mover()
