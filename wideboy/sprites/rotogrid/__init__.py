import logging
from pygame import Clock, Color, Event, Rect
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_grid


logger = logging.getLogger("sprite.rotogrid")


class RotoGridSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        color_fg: Color = Color(255, 255, 255, 255),
        color_bg: Color = Color(0, 0, 0, 0),
        spacing: float = 10,
        line_size: int = 1,
        zoom_speed: float = 0.1,
        zoom_range: tuple[float, float] = (1.0, 1.1),
        rotate_speed: int = 1,
        rotate_range: tuple[int, int] = (-5, 5),
    ) -> None:
        super().__init__(scene, rect)
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.spacing = spacing
        self.line_size = line_size
        self.zoom_speed = zoom_speed
        self.zoom_range = zoom_range
        self.rotate_speed = rotate_speed
        self.rotate_range = rotate_range
        self.scale = self.zoom_range[0]
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
        if self.angle < self.rotate_range[0] or self.angle > self.rotate_range[1]:
            self.rotate_speed *= -1
        self.dirty = 1
        self.render()

    def render(self) -> None:
        self.image = render_grid(
            (self.rect.width, self.rect.width),
            self.spacing,
            self.color_fg,
            self.scale,
            self.angle,
        )
