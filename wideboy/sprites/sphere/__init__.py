import logging
import math
import pygame
from pygame import Clock, Color, Event, Rect, Surface
from typing import Tuple
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.sphere")


class SphereSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        radius: int = 100,
        rotate_speed: int = 1,
    ) -> None:
        super().__init__(scene, rect)
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.radius = radius
        self.rotate_speed = rotate_speed
        self.rotate_position: Tuple[int, int, int] = (0, 0, 0)

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        self.rotate_sphere()

    def create_sphere_image(self):
        image = Surface((self.radius * 2, self.radius * 2))
        image.fill(self.color_bg)
        for lat in range(-90, 90, 10):
            for lon in range(0, 360, 10):
                x = (
                    self.radius
                    * math.sin(math.radians(lat))
                    * math.cos(math.radians(lon))
                )
                y = (
                    self.radius
                    * math.sin(math.radians(lat))
                    * math.sin(math.radians(lon))
                )
                z = self.radius * math.cos(math.radians(lat))
                x, y, z = self.rotate_point(x, y, z)
                x += self.radius
                y += self.radius
                pygame.draw.circle(image, self.color_fg, (int(x), int(y)), 1)
        return image

    def rotate_point(self, x, y, z):
        x_rot = x * math.cos(math.radians(self.rotate_position[0])) + z * math.sin(
            math.radians(self.rotate_position[0])
        )
        y_rot = y * math.cos(math.radians(self.rotate_position[1])) + z * math.sin(
            math.radians(self.rotate_position[1])
        )
        z_rot = (
            z * math.cos(math.radians(self.rotate_position[2]))
            - x * math.sin(math.radians(self.rotate_position[0]))
            - y * math.sin(math.radians(self.rotate_position[1]))
        )
        return x_rot, y_rot, z_rot

    def rotate_sphere(self):
        self.rotate_position = (
            self.rotate_position[0] + self.rotate_speed,
            self.rotate_position[1] + 0,
            self.rotate_position[2] + self.rotate_speed,
        )
        self.image = self.create_sphere_image()
        self.dirty = 1
