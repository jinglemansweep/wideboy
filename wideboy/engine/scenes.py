import logging
from pygame import Clock, Rect
from typing import List, Optional, Type, TYPE_CHECKING
from wideboy.constants import EVENT_HASS_ENTITY_UPDATE
from wideboy.scenes.base import BaseScene
from wideboy.utils.helpers import post_event

if TYPE_CHECKING:
    from wideboy.engine import Engine

logger = logging.getLogger("scenes")


class SceneManager:
    scenes: list[BaseScene] = list()
    scene: Optional[BaseScene] = None
    index: int = 0

    def __init__(self, engine: "Engine") -> None:
        logger.debug(f"manager:init engine={engine}")
        self.engine = engine

    def load_scenes(self, scenes: List[Type[BaseScene]]) -> None:
        self.scenes = [SceneCls(self.engine) for SceneCls in scenes]
        self.set_scene(0)

    def change_scene(self, name: str):
        index = self.get_scene_id_by_name(name)
        if index is not None:
            self.set_scene(index)

    def set_scene(self, index: int):
        logger.info(f"manager:set index={index}")
        if self.scene:
            self.scene.destroy()
        self.index = index
        self.scene = self.scenes[self.index]
        post_event(
            EVENT_HASS_ENTITY_UPDATE,
            name="scene_select",
            state=dict(selected_option=self.scene.name),
        )
        self.scene.setup()

    def next_scene(self) -> None:
        next_index = self.index + 1
        if next_index >= len(self.scenes):
            next_index = 0
        print("NEXT INDEX", next_index)
        self.set_scene(next_index)

    def get_scene_names(self) -> List[str]:
        return [scene.name for scene in self.scenes]

    def get_scene_id_by_name(self, name: str) -> Optional[int]:
        for i, scene in enumerate(self.scenes):
            if name == scene.name:
                print(name, i)
                return i
        return None

    @property
    def frame(self) -> Optional[int]:
        if not self.scene:
            return None
        return self.scene.frame

    def render(self, *args, **kwargs) -> Optional[list[Rect]]:
        if not self.scene:
            logger.debug("SceneManager: no scene loaded")
            return []
        return self.scene.render(*args, **kwargs)

    def debug(self, clock: Clock, delta: float):
        if not self.scene:
            return
        return self.scene.debug(clock, delta)
