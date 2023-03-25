import logging
import pygame
from typing import Optional
from .base import BaseScene
from wideboy.state import StateStore


logger = logging.getLogger(__name__)


class SceneManager:
    scenes: set[BaseScene]

    def __init__(self) -> None:
        self.scenes = set()
        self.scene_index: Optional[int] = None

    def add(self, scene: BaseScene) -> None:
        if not len(self.scenes):
            self.scene_index = 0
        self.scenes.add(scene)

    def run(self, name: str) -> None:
        idx = self._find_scene(name)
        if idx:
            self.scene_index = idx

    def next(self) -> None:
        if not self.scene_index:
            return
        next_idx: int = self.scene_index + 1
        if next_idx + 1 > len(self.scenes):
            next_idx = 0
        self._change_scene(next_idx)
        if self.scene:
            self.scene.setup()

    def _change_scene(self, idx: int):
        self.scene_index = idx

    def _find_scene(self, name: str) -> Optional[int]:
        for i, scene in enumerate(self.scenes):
            if name == scene.name:
                return i
        return None

    @property
    def scene(self) -> Optional[BaseScene]:
        if not len(self.scenes) or not self.scene_index:
            return None
        return list(self.scenes)[self.scene_index]

    @property
    def frame(self) -> Optional[int]:
        if not self.scene:
            return None
        return self.scene.frame

    def update(self, *args, **kwargs):
        self.scene.update(*args, **kwargs)

    def render(self, *args, **kwargs):
        if not self.scene:
            return
        return self.scene.render(*args, **kwargs)

    def debug(self, clock: pygame.time.Clock, delta: float):
        if not self.scene:
            return
        return self.scene.debug(clock, delta)
