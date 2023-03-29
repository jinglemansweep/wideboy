import logging
import pygame

from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("scenes.scene.blank")


class FillSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
    ) -> None:
        super().__init__(rect)
        self.image = pygame.surface.Surface((self.rect.width, self.rect.height))
        self.image.fill((0, 0, 0))
        self.dirty = 2


class BlankScene(BaseScene):
    name = "blank"

    def __init__(
        self,
        surface: pygame.surface.Surface,
        bg_color: pygame.color.Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, bg_color)
        self.group.add(FillSprite(pygame.Rect(0, 0, self.width, self.height)))
