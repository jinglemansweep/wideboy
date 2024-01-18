from ecs_pattern import EntityManager, System
from ..components import ComMotion, ComVisible


class SysMovement(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities

    def update(self):
        for movable_entity in self.entities.get_with_component(ComMotion, ComVisible):
            movable_entity.x += movable_entity.speed_x
            movable_entity.y += movable_entity.speed_y
