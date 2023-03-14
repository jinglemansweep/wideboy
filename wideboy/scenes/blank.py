import logging
import pygame

from wideboy.scenes._base import BaseScene
from wideboy.sprites._base import BaseSprite
from wideboy.utils.state import StateStore


logger = logging.getLogger(__name__)


class FillSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        state: StateStore,
    ) -> None:
        super().__init__(rect, state)
        self.image = pygame.surface.Surface((self.rect.width, self.rect.height))
        self.image.fill((0, 0, 0))
        self.dirty = 2


class BlankScene(BaseScene):
    name = "blank"

    def __init__(
        self,
        surface: pygame.surface.Surface,
        state: StateStore,
        bg_color: pygame.color.Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, state, bg_color)
        self.group.add(FillSprite((0, 0, self.width, self.height), state))
