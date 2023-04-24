import logging
import pygame
from pytweening import easeInOutSine
from typing import Optional, Any

from wideboy.sprites.base import BaseSprite

logger = logging.getLogger("scenes.animation")


class Act(pygame.sprite.Sprite):
    def __init__(
        self,
        duration: int,
        actions: Optional[list[Any]] = None,
        run_now: bool = True,
    ) -> None:
        super().__init__()
        self.duration = duration
        self.actions = actions or []
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
            self.kill()


class Animation:
    def __init__(
        self,
        sprite: BaseSprite,
        target: pygame.math.Vector2,
        duration: int,
        origin: Optional[pygame.math.Vector2] = None,
        tweener=easeInOutSine,
    ) -> None:
        self.sprite: BaseSprite = sprite
        self.tweener = tweener
        self.target: pygame.math.Vector2 = target
        self.duration: int = duration
        self.current: pygame.math.Vector2
        assert self.sprite.rect is not None
        self.current = origin or pygame.math.Vector2(
            self.sprite.rect.x,
            self.sprite.rect.y,
        )
        self.origin: pygame.math.Vector2 = self.current
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
        if not self.is_moving() or self.index is None:
            return None
        self.index += 1
        ri = self.index / self.duration
        tween_val = self.tweener(ri)
        x = self.origin[0] + (self.distances[0] * tween_val)
        y = self.origin[1] + (self.distances[1] * tween_val)
        if self.index < self.duration - 1:
            self.current = pygame.math.Vector2(x, y)
        else:
            self.current = self.target
        assert self.sprite.rect is not None
        self.sprite.rect.x, self.sprite.rect.y = int(self.current[0]), int(
            self.current[1]
        )
        self.sprite.dirty = 1
