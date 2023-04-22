import logging
from pygame import Rect, Vector2
from typing import Optional
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import (
    load_image,
    filter_surface,
    scale_surface,
)


logger = logging.getLogger("sprite.image")


class ImageSprite(BaseSprite):
    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        size: Optional[Vector2],
        filename: str,
        alpha: int = 255,
    ) -> None:
        super().__init__(scene, rect)
        self.filename = filename
        self.size = size
        self.alpha = alpha
        self.render()

    def render(self) -> None:
        surface = load_image(self.filename)
        self.rect = Rect(
            self.rect[0], self.rect[1], surface.get_rect()[2], surface.get_rect()[3]
        )
        surface = scale_surface(surface, self.size)
        surface = filter_surface(surface, alpha=self.alpha)
        self.image = surface
        self.dirty = 1
