from dataclasses import field
from ecs_pattern import component
from pygame import Surface
from pygame.sprite import Sprite
from typing import List, Optional, Tuple


@component
class ComponentIdentifiable:
    id: str


@component
class ComponentVisible:
    sprite: Sprite
    x: int = 0
    y: int = 0
    z_order: int = 0
    hidden: bool = False


@component
class ComponentAlpha:
    alpha: int = 255


@component
class ComponentMotion:
    speed_x: int = 0
    speed_y: int = 0
    direction_x: int = 0
    direction_y: int = 0


@component
class ComponentTarget:
    target_x: Optional[int] = None
    target_y: Optional[int] = None


@component
class ComponentBound:
    bound_mode: str = "bounce"
    bound_rect: Optional[Tuple[int, int, int, int]] = None
    bound_size: Optional[Tuple[int, int]] = None


@component
class ComponentFade:
    fade_target_alpha: Optional[int] = None
    fade_speed: int = 8


@component
class ComponentFrame:
    frames: List[Surface] = field(default_factory=list)
    scene_frame: int = 0
    frame_index: int = 0
    frame_direction: int = 1
    frame_delay: int = 1
