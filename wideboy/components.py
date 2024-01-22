from ecs_pattern import component
from pygame.sprite import Sprite
from typing import Optional, Tuple


@component
class ComVisible:
    sprite: Sprite
    x: int = 0
    y: int = 0
    z_order: int = 0
    alpha: int = 255
    hidden: bool = False


@component
class ComMotion:
    speed_x: int = 0
    speed_y: int = 0


@component
class ComTarget:
    target_x: Optional[int] = None
    target_y: Optional[int] = None


@component
class ComBound:
    bound_mode: str = "bounce"
    bound_rect: Optional[Tuple[int, int, int, int]] = None
    bound_size: Optional[Tuple[int, int]] = None


@component
class ComFade:
    fade_target_alpha: Optional[int] = None
    fade_speed: int = 8
