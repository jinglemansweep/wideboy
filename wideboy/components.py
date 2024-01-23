from dataclasses import field
from ecs_pattern import component
from pygame import Surface
from pygame.sprite import Sprite
from typing import List, Optional, Tuple


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
    direction_x: int = 0
    direction_y: int = 0


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


@component
class ComFrame:
    frames: List[Surface] = field(default_factory=list)
    scene_frame: int = 0
    frame_index: int = 0
    frame_direction: int = 1
    frame_delay: int = 1
