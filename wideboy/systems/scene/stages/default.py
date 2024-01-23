import logging
from ecs_pattern import EntityManager
from pathlib import Path
from pygame.image import load as pygame_image_load
from typing import List, Tuple
from ....consts import EventTypes
from ....entities import (
    AppState,
    WidgetClockDate,
    WidgetClockTime,
    WidgetSlideshow,
    WidgetTileGrid,
)
from ..sprites import build_slideshow_sprite
from . import Stage


logger = logging.getLogger(__name__)


class StageDefault(Stage):
    slideshow_images: List[Path] = []
    slideshow_index: int = 0

    def __init__(
        self,
        entities: EntityManager,
        display_size: Tuple[int, int],
    ) -> None:
        super().__init__(entities)
        self.display_size = display_size
        self.setup()

    def setup(self) -> None:
        self._glob_backgrounds()
        self.stage_entities.append(
            WidgetSlideshow(
                build_slideshow_sprite(
                    pygame_image_load(self.slideshow_images[self.slideshow_index])
                )
            )  # type: ignore[call-arg]
        )

        for w in self.entities.get_by_class(
            WidgetClockDate,
            WidgetClockTime,
            WidgetTileGrid,
        ):
            w.fade_target_alpha = 255

    def update(self) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        for event_type, event_payload in app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                self.advance()

    def advance(self) -> None:
        widget_slideshow = next(self.entities.get_by_class(WidgetSlideshow))
        self.slideshow_index += 1
        if self.slideshow_index >= len(self.slideshow_images):
            self.slideshow_index = 0
        widget_slideshow.sprite.set_next_image(
            pygame_image_load(self.slideshow_images[self.slideshow_index])
        )
        widget_slideshow.sprite.swap()

    def _glob_backgrounds(self) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        self.slideshow_images = list(
            Path(app_state.config.paths.images_backgrounds).glob("*.png")
        )
