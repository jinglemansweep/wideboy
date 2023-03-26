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
        scene_id = self.get_scene_id_by_name(name)
        self.set_scene(scene_id)

    def set_scene(self, idx: Optional[int]):
        if not idx:
            return
        logger.info(f"scene:set index={idx}")
        self.scene_index = idx
        self.scene.setup()

    def next_scene(self) -> None:
        next_index = self.scene_index + 1
        if next_index >= len(self.scenes):
            next_index = 0
        self.set_scene(next_index)

    def get_scene_id_by_name(self, name: str) -> Optional[int]:
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
