import logging
from ecs_pattern import EntityManager, System
from pygame.surface import Surface
from ..components import ComVisible

logger = logging.getLogger(__name__)


class SysDraw(System):
    def __init__(self, entities: EntityManager, screen: Surface) -> None:
        self.entities = entities
        self.screen = screen

    def start(self) -> None:
        logger.info("Draw system starting...")

    def update(self) -> None:
        self.screen.fill((0, 0, 0))
        visible_entities = self.entities.get_with_component(ComVisible)
        sorted_visible = sorted(visible_entities, key=lambda x: x.z_order)

        for e in sorted_visible:
            self.screen.blit(e.sprite.image, (e.x, e.y))
