from ecs_pattern import EntityManager, System
from pygame.surface import Surface
from ..components import ComVisible


class SysDraw(System):
    def __init__(self, entities: EntityManager, screen: Surface):
        self.entities = entities
        self.screen = screen

    def update(self):
        self.screen.fill((0, 0, 0))
        for visible_entity in self.entities.get_with_component(ComVisible):
            self.screen.blit(
                visible_entity.sprite.image, (visible_entity.x, visible_entity.y)
            )
