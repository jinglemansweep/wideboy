import logging
from pygame import Rect
from pygame.sprite import DirtySprite
from typing import Any
from wideboy.scenes.base import BaseScene

logger = logging.getLogger("sprites.base")


class BaseSprite(DirtySprite):
    def __init__(self, scene: BaseScene, rect: Rect) -> None:
        super().__init__()
        self.scene = scene
        self.rect = rect

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
