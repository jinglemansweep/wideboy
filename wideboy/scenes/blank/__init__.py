import logging
from pygame import Rect, Color, Surface

from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("scenes.scene.blank")


class FillSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height))
        self.image.fill((0, 0, 0))
        self.dirty = 2


class BlankScene(BaseScene):
    name = "blank"

    def __init__(
        self,
        surface: Surface,
        bg_color: Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, bg_color)
        self.group.add(FillSprite(Rect(0, 0, self.width, self.height)))
