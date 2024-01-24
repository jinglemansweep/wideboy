import logging
from ecs_pattern import EntityManager
from typing import Tuple
from . import Stage


logger = logging.getLogger(__name__)


class StageBoot(Stage):
    def __init__(self, entities: EntityManager, display_size: Tuple[int, int]) -> None:
        super().__init__(entities)
        self.display_size = display_size
        self.setup()
