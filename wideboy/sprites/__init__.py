import logging
import pygame
from pytweening import easeInOutSine
from typing import Optional, Any

from wideboy.utils.state import StateStore

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
        self.loop = loop
        self.act_time_index = 0 if run_now else None

    def add_action(
        self,
        time_index: int,
        action: tuple[int, Any],
    ) -> None:
        self.actions.append((time_index, action))

    def start(self) -> None:
        self.act_time_index = 0

    def update(self) -> None:
        if self.act_time_index is not None:
            for time_index, action in self.actions:
                if isinstance(action, Animation):
                    if time_index == self.act_time_index:
                        action.start()
                    action.update()
                else:
                    if time_index == self.act_time_index:
                        action()
            self.act_time_index += 1
        if self.act_time_index == self.duration - 1:
            self.act_time_index = 0 if self.loop else None


class Animation:
    def __init__(
        self,
        sprite: pygame.sprite.Sprite,
        target: tuple[int, int],
        duration: int,
        origin: Optional[tuple[int, int]] = None,
        tweener=easeInOutSine,
    ) -> None:
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
        logger.debug(
            f"sprite::animation target={self.target} origin={self.origin} duration={self.duration} distances={self.distances}"
        )

    def start(self) -> None:
        self.index = 0

    def is_moving(self) -> bool:
        return self.index is not None and self.index < self.duration

    def update(self) -> None:
        if not self.is_moving():
            return
        self.index += 1
        ri = self.index / self.duration
        tween_val = self.tweener(ri)
        x = self.origin[0] + (self.distances[0] * tween_val)
        y = self.origin[1] + (self.distances[1] * tween_val)
        if self.index < self.duration - 1:
            self.current = (x, y)
        else:
            self.current = self.target
        self.sprite.rect.x, self.sprite.rect.y = self.current
        self.sprite.dirty = 1


class BaseSprite(pygame.sprite.DirtySprite):
    def __init__(self, rect: pygame.rect.Rect, state: StateStore) -> None:
        super().__init__()
        self.rect = pygame.rect.Rect(*rect)
        self.state = state

    def update(self, *args, **kwargs) -> None:
        super().update(*args, **kwargs)
