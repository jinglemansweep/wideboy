import logging
import pygame
from typing import Optional
from .base import BaseScene
from wideboy.state import StateStore


logger = logging.getLogger(__name__)


class SceneManager:
    scenes: set[BaseScene]

    def __init__(self, scenes: set[BaseScene]) -> None:
        self.scenes: set[BaseScene] = scenes
        self.scene_index: int = 0

    def change_scene(self, name: str):
        scene_id = self.find_scene(name)
        if scene_id:
            self.scene_index = scene_id
            self.scene.setup()

    def find_scene(self, name: str) -> Optional[int]:
        for i, scene in enumerate(self.scenes):
            if name == scene.name:
                return i
        return None

    @property
    def scene(self) -> BaseScene:
        return list(self.scenes)[self.scene_index]

    @property
    def frame(self) -> Optional[int]:
        if not self.scene:
            return None
        return self.scene.frame

    def update(self, *args, **kwargs):
        self.scene.update(*args, **kwargs)

    def render(self, *args, **kwargs) -> Optional[list[pygame.rect.Rect]]:
        if not self.scene:
            return []
        return self.scene.render(*args, **kwargs)

    def debug(self, clock: pygame.time.Clock, delta: float):
        if not self.scene:
            return
        return self.scene.debug(clock, delta)
