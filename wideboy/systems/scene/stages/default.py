import logging
import random
from ecs_pattern import EntityManager
from pathlib import Path
from pygame import Color, Surface
from typing import List, Tuple
from ....consts import EventTypes
from ....entities import (
    AppState,
    Cache,
    UIEntity,
)
from ....utils import read_yaml
from ....sprites.graphics import load_image, recolor_image
from ....sprites.slideshow import Transition
from ..sprites import build_slideshow_sprite
from . import Stage


logger = logging.getLogger(__name__)


class StageDefault(Stage):
    slideshow_images: List[Path] = []
    slideshow_timer: int = 0

    def __init__(
        self,
        entities: EntityManager,
        display_size: Tuple[int, int],
    ) -> None:
        super().__init__(entities)
        self.entities = entities
        self.display_size = display_size
        self.setup()

    def setup(self) -> None:
        self.app_state = next(self.entities.get_by_class(AppState))
        self.cache = next(self.entities.get_by_class(Cache))

        scene_config = read_yaml(self.app_state.config.scenes.file)
        logger.debug(f"Scene config: {scene_config}")

        self.slideshow_timer = self.app_state.slideshow_interval
        self._glob_backgrounds(randomize=True)

        # Add slideshow widget
        slideshow_image = self._load_and_process_image(
            self.slideshow_images[self.app_state.slideshow_index]
        )
        self.stage_entities.append(
            UIEntity(
                "slideshow",
                build_slideshow_sprite(slideshow_image, self.display_size),
            )  # type: ignore[call-arg]
        )

        # Fade in widgets
        for w in self.entities.get_by_class(
            UIEntity,
        ):
            w.fade_target_alpha = 255

    def update(self) -> None:
        ui_entities = self.entities.get_by_class(UIEntity)
        widget_slideshow = next(filter(lambda e: e.id == "slideshow", ui_entities))
        # widget_spinner = next(self.entities.get_by_class(WidgetSpinner))
        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                self.slideshow_timer -= 1
                if self.slideshow_timer <= 0:
                    logger.debug("sys.scene.stage.default.slideshow: advance")
                    self.advance()
                    self.slideshow_timer = self.app_state.slideshow_interval

        widget_slideshow.sprite.update()

    def advance(self) -> None:
        ui_entities = self.entities.get_by_class(UIEntity)
        widget_slideshow = next(filter(lambda e: e.id == "slideshow", ui_entities))
        self.app_state.slideshow_index += 1
        if self.app_state.slideshow_index >= len(self.slideshow_images):
            self.app_state.slideshow_index = 0
        next_image = self._load_and_process_image(
            self.slideshow_images[self.app_state.slideshow_index]
        )
        widget_slideshow.sprite.set_next_image(next_image)
        widget_slideshow.sprite.swap(
            random.choice([Transition.FADE, Transition.WIPE, Transition.FOLD])
        )

    def _glob_backgrounds(self, randomize: bool = False) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        images = list(Path(app_state.config.paths.images_backgrounds).glob("*.png"))
        if randomize:
            random.shuffle(images)
        self.slideshow_images = images

    def _load_and_process_image(self, filename: str) -> Surface:
        tint_enabled = self.app_state.tint_enabled
        color = self.app_state.tint_color
        brightness = self.app_state.tint_brightness
        color = Color(
            color[0] * brightness / 255,
            color[1] * brightness / 255,
            color[2] * brightness / 255,
        )
        surface = load_image(filename)
        if tint_enabled:
            surface = recolor_image(surface, color)
        return surface
