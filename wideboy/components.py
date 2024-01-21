from ecs_pattern import component
from pygame.sprite import Sprite
from typing import Optional


@component
class ComVisible:
    sprite: Sprite
    x: int = 0
    y: int = 0
    z_order: int = 0


@component
class ComMotion:
    speed_x: int = 0
    speed_y: int = 0


@component
class ComTarget:
    target_x: Optional[int] = None
    target_y: Optional[int] = None
