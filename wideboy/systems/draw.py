import logging
import os
from datetime import datetime
from ecs_pattern import EntityManager, System
from pygame.image import save as pygame_image_save
from pygame.surface import Surface
from ..components import ComponentVisible
from ..entities import AppState

logger = logging.getLogger(__name__)


class SysDraw(System):
    def __init__(self, entities: EntityManager, screen: Surface) -> None:
        self.entities = entities
        self.screen = screen

    def start(self) -> None:
        logger.info("Draw system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        self.screen.fill((0, 0, 0))
        visible_entities = self.entities.get_with_component(ComponentVisible)
        sorted_visible = sorted(visible_entities, key=lambda x: x.z_order)

        for e in sorted_visible:
            if e.hidden:
                continue
            self.screen.blit(e.sprite.image, (e.x, e.y))

        if self.app_state.screenshot:
            self.screenshot()
            self.app_state.screenshot = False

    def screenshot(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"screenshot_{timestamp}.png"
        output_file = os.path.join(
            self.app_state.config.paths.images_screenshots, filename
        )
        logger.info(f"sys.draw.screenshot: output={output_file}")
        pygame_image_save(self.screen, output_file)
