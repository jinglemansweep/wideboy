import logging
import pygame
import random
from typing import Optional
from pygame import Clock, Color, Event, Rect, Surface, Vector2, SRCALPHA
from pygame.sprite import Group, Sprite
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.rotogrid")


class RotoGridSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        grid_size: int = 20,
        line_size: int = 1,
        zoom_speed: float = 0.01,
        zoom_range: tuple[float, float] = (1.0, 5.0),
        rotate_speed: int = 1,
        angle_range: tuple[int, int] = (-5, 5),
    ) -> None:
        super().__init__(scene, rect)
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.grid_size = grid_size
        self.line_size = line_size
        self.zoom_speed = zoom_speed
        self.zoom_range = zoom_range
        self.rotate_speed = rotate_speed
        self.angle_range = angle_range
        self.image_grid = self.draw_grid(
            (self.rect.width, self.rect.height),  # square based on width
            self.color_fg,
            grid_size=self.grid_size,
            line_size=self.line_size
        )
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.scale = 1.5
        self.angle = 0

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        self.scale += self.zoom_speed
        if self.scale < self.zoom_range[0] or self.scale > self.zoom_range[1]:
            self.zoom_speed *= -1
        self.angle += self.rotate_speed
        if self.angle < self.angle_range[0] or self.angle > self.angle_range[1]:
            self.rotate_speed *= -1
        self.dirty = 1
        self.render()

    def render(self) -> None:
        self.image = pygame.transform.rotozoom(self.image_grid, self.angle, self.scale)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw_grid(
        self,
        size: Vector2,
        color: Color = Color(255, 255, 255, 255),
        grid_size=10,
        line_size=1,
    ) -> Surface:
        surface = Surface(size, SRCALPHA)
        for i in range(0, size[0], grid_size):
            pygame.draw.line(surface, color, (i, 0), (i, size[1]), line_size)
        for i in range(0, size[1], grid_size):
            pygame.draw.line(surface, color, (0, i), (size[0], i), line_size)
        return surface
