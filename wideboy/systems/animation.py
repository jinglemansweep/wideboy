import logging
from ecs_pattern import EntityManager, System
from ..components import ComMotion, ComVisible

logger = logging.getLogger(__name__)


class SysMovement(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Movement system starting...")

    def update(self) -> None:
        for movable_entity in self.entities.get_with_component(ComMotion, ComVisible):
            movable_entity.x += movable_entity.speed_x
            movable_entity.y += movable_entity.speed_y
