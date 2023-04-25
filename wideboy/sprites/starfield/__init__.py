import logging
import pygame
import random
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from pygame.sprite import Group, Sprite
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.starfield")


class StarfieldSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        star_count: int = 20,
        star_size_range: tuple[int, int] = (1, 2),
        layer_count: int = 3,
        scroll_speed: int = 1,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
    ) -> None:
        super().__init__(scene, rect)
        self.star_count = star_count
        self.star_size_range = star_size_range
        self.layer_count = layer_count
        self.scroll_speed = scroll_speed
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.star_groups = [Group() for i in range(self.layer_count)]
        self.add_stars()
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        self.update_stars()
        self.render()

    def add_stars(self) -> None:
        for star_group in self.star_groups:
            for i in range(self.star_count):
                star = Sprite()
                star.image = self.generate_star()
                star.rect = star.image.get_rect()
                star.rect.x = random.randint(0, self.rect.width)
                star.rect.y = random.randint(0, self.rect.height)
                star_group.add(star)

    def update_stars(self):
        for layer_index, star_group in enumerate(self.star_groups):
            for star in star_group:
                star.rect.x -= self.scroll_speed * (layer_index + 1)
                if star.rect.right < 0:
                    star.rect.x = self.rect.width
                    star.rect.y = random.randint(0, self.rect.height)

    def generate_star(self) -> Surface:
        size = random.randint(self.star_size_range[0], self.star_size_range[1])
        image = Surface((size, size), SRCALPHA)
        pygame.draw.circle(
            image,
            self.color_fg,
            (size / 2, size / 2),
            1,
        )
        return image

    def render(self) -> None:
        self.image.fill(self.color_bg)
        for star_group in self.star_groups:
            star_group.draw(self.image)
        self.dirty = 1
