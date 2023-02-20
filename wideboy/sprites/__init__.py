import logging
import pygame
from pytweening import easeInOutSine
from typing import Optional, Any

logger = logging.getLogger(__name__)


class Act:
    def __init__(
        self,
        duration: int,
        actions: Optional[list[Any]] = None,
        loop: bool = False,
        run_now: bool = True,
    ) -> None:
        self.duration = duration
        self.actions = actions or []
        # 0, Animation(sprite, dest, source=None, duration=100)
        # 100, ...
        self.loop = loop
        self.act_time_index = 0
        if run_now:
            self.running = True

    def add_action(
        self,
        time_index: int,
        action: tuple[int, Any],
    ) -> None:
        self.actions.append((time_index, action))

    def run(self):
        self.running = True

    def update(self):
        if self.running:
            for time_index, action in self.actions:
                # print(time_index, action)
                if time_index == self.act_time_index:
                    action.run()
                action.update()
            self.act_time_index += 1
        if self.act_time_index == self.duration:
            if self.loop:
                self.act_time_index = 0
            else:
                self.running = False


class Animation:
    def __init__(
        self,
        sprite: pygame.sprite.Sprite,
        target: tuple[int, int],
        duration: int,
        origin: Optional[tuple[int, int]] = None,
        tweener=easeInOutSine,
    ):
        self.sprite: pygame.sprite.Sprite = sprite
        self.tweener = tweener
        self.target: tuple[int, int] = target
        self.duration: int = duration
        if origin is not None:
            self.current = origin
        else:
            self.current: tuple[int, int] = self.sprite.rect.x, self.sprite.rect.y
        self.origin = self.current
        self.distances = (
            (self.target[0] - self.origin[0]),
            (self.target[1] - self.origin[1]),
        )
        self.index: Optional[int] = None
        self.running: bool = False
        logger.debug(
            f"sprite::animation target={self.target} origin={self.origin} duration={self.duration} distances={self.distances}"
        )

    def run(self):
        self.index = 0
        # self.current = self.origin

    def is_moving(self):
        return self.index is not None and self.index < self.duration

    def update(self):
        print(self.index)
        if not self.is_moving():
            return
        ri = self.index / self.duration
        tween_val = self.tweener(ri)
        x = self.origin[0] + (self.distances[0] * tween_val)
        y = self.origin[1] + (self.distances[1] * tween_val)
        if self.index != self.duration:
            self.current = (x, y)
        else:
            self.current = self.target
        self.sprite.rect.x, self.sprite.rect.y = self.current
        self.sprite.dirty = 1
        self.index += 1


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
        return self.index is not None and self.index <= self.length

    def tick(self, update_sprite=True):
        if not self.is_moving():
            return
        ri = self.index / self.length
        tween_val = self.tweener(ri)
        x = self.origin[0] + (self.distances[0] * tween_val)
        y = self.origin[1] + (self.distances[1] * tween_val)
        if self.index != self.length:
            self.current = (x, y)
        else:
            self.current = self.target
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
