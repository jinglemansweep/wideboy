import logging
from pygame import Clock, Rect
from typing import Optional
from wideboy.constants import EVENT_SCENE_MANAGER_NEXT
from wideboy.scenes.base import BaseScene


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

    def get_scene_names(self) -> list[str]:
        return [scene.name for scene in self.scenes]

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

    def render(self, *args, **kwargs) -> Optional[list[Rect]]:
        if not self.scene:
            return []
        return self.scene.render(*args, **kwargs)

    def debug(self, clock: Clock, delta: float):
        if not self.scene:
            return
        return self.scene.debug(clock, delta)
