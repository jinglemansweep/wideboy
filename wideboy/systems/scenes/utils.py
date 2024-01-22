from ecs_pattern import entity
from typing import List


class Stage:
    entities: List[entity]

    def setup(self) -> None:
        pass
