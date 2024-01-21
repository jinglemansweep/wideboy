import logging
from ecs_pattern import EntityManager, System
from ..components import ComMotion, ComTarget, ComVisible

logger = logging.getLogger(__name__)


class SysMovement(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Movement system starting...")

    def update(self) -> None:
        # Targeting

        for e in self.entities.get_with_component(ComTarget, ComMotion, ComVisible):
            # X Axis
            if e.target_x is not None:
                if e.x < e.target_x:
                    e.speed_x = 1
                elif e.x > e.target_x:
                    e.speed_x = -1
                else:
                    e.target_x = None
                    e.speed_x = 0

            # Y Axis
            if e.target_y is not None:
                if e.y < e.target_y:
                    e.speed_y = 1
                elif e.y > e.target_y:
                    e.speed_y = -1
                else:
                    e.target_y = None
                    e.speed_y = 0

        # Movement

        for e in self.entities.get_with_component(ComMotion, ComVisible):
            e.x += e.speed_x
            e.y += e.speed_y
