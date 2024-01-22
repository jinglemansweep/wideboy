from ecs_pattern import EntityManager, entity
from typing import List


class Stage:
    entities: EntityManager
    stage_entities: List[entity]

    def __init__(self, entities: EntityManager, *args, **kwargs) -> None:
        self.entities = entities
        self.stage_entities = []

    def setup(self) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        pass
