from typing import Optional
from wideboy.scenes import BaseScene


class Director:
    def __init__(self) -> None:
        self.scenes = {}
        self.active_scene: Optional[str] = None

    def add_scene(self, name: str, scene: BaseScene) -> None:
        self.scenes[name] = scene

    def change_scene(self, name: str) -> None:
        self.active_scene = name

    @property
    def scene(self) -> Optional[BaseScene]:
        return self.scenes.get(self.active_scene)

    def update(self, *args, **kwargs):
        self.scene.update(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self.scene.render(*args, **kwargs)
