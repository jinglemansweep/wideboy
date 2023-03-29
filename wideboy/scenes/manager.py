import logging
import pygame
from typing import Optional
from .base import BaseScene


logger = logging.getLogger("scenes.manager")


class SceneManager:
    scenes: list[BaseScene] = list()
    scene: Optional[BaseScene] = None
    index: int = 0

    def __init__(self, scenes: list[BaseScene]) -> None:
        self.scenes: list[BaseScene] = scenes
        self.set_scene(0)

    def change_scene(self, name: str):
        index = self.get_scene_id_by_name(name)
        self.set_scene(index)

    def set_scene(self, index: int):
        logger.info(f"scene:set index={index}")
        if self.scene:
            self.scene.destroy()
        self.index = index
        self.scene = self.scenes[self.index]
        self.scene.setup()

    def next_scene(self) -> None:
        next_index = self.index + 1
        if next_index >= len(self.scenes):
            next_index = 0
        self.set_scene(next_index)

    def get_scene_id_by_name(self, name: str) -> Optional[int]:
        for i, scene in enumerate(self.scenes):
            if name == scene.name:
                return i
        return None

    @property
    def frame(self) -> Optional[int]:
        if not self.scene:
            return None
        return self.scene.frame

    def update(
        self, clock: pygame.time.Clock, delta: float, events: list[pygame.event.Event]
    ) -> None:
        if not self.scene:
            return None
        self.scene.update(clock, delta, events)

    def draw(self, *args, **kwargs) -> Optional[list[pygame.rect.Rect]]:
        if not self.scene:
            return []
        return self.scene.draw(*args, **kwargs)

    def debug(self, clock: pygame.time.Clock, delta: float):
        if not self.scene:
            return
        return self.scene.debug(clock, delta)
