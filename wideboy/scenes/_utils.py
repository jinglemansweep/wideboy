import logging
import pygame
from typing import Optional
from wideboy.scenes._base import BaseScene
from wideboy.utils.state import StateStore


logger = logging.getLogger(__name__)


class SceneManager:
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
        next_idx = self.scene_index + 1
        if next_idx + 1 > len(self.scenes):
            next_idx = 0
        self._change_scene(next_idx)
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
        if not len(self.scenes):
            return None
        return list(self.scenes)[self.scene_index]

    @property
    def frame(self) -> int:
        return self.scene.frame

    def update(self, *args, **kwargs):
        self.scene.update(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self.scene.render(*args, **kwargs)

    def debug(self, clock: pygame.time.Clock, delta: float):
        return self.scene.debug(self.frame, clock, delta)
