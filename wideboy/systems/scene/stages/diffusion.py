import logging
from ecs_pattern import EntityManager
from typing import Tuple
from ....consts import EventTypes
from ....entities import (
    AppState,
    Cache,
    WidgetAnimatedGif,
    WidgetClockDate,
    WidgetClockTime,
    WidgetTileGrid,
)
from ..sprites import build_image_sprite
from . import Stage

logger = logging.getLogger(__name__)

IMAGE_CACHE_KEYS = [
    "gif_diffusion_border_terriers",
    "gif_diffusion_monolith",
    "gif_diffusion_neon_city",
]


class StageDiffusion(Stage):
    def __init__(
        self,
        entities: EntityManager,
        display_size: Tuple[int, int],
    ) -> None:
        super().__init__(entities)
        self.display_size = display_size
        self.setup()

    def setup(self) -> None:
        self.app_state = next(self.entities.get_by_class(AppState))
        self.cache = next(self.entities.get_by_class(Cache))
        self.cache_keys = IMAGE_CACHE_KEYS
        self.cache_index = 0

        self.stage_entities.append(
            WidgetAnimatedGif(
                build_image_sprite(
                    self.cache.surfaces[self.cache_keys[self.cache_index]][0]
                ),
                x=0,
                y=0,
                z_order=5,
                frames=self.cache.surfaces[self.cache_keys[self.cache_index]],
                frame_delay=1,
            ),  # type: ignore[call-arg]
        )

        for w in self.entities.get_by_class(
            WidgetClockDate,
            WidgetClockTime,
            WidgetTileGrid,
        ):
            w.fade_target_alpha = 255

    def update(self) -> None:
        widget_animated_gif = next(self.entities.get_by_class(WidgetAnimatedGif))
        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_MINUTE:
                self.cache_index += 1
                if self.cache_index >= len(self.cache_keys):
                    self.cache_index = 0
                widget_animated_gif.frames = self.cache.surfaces[
                    self.cache_keys[self.cache_index]
                ]
                widget_animated_gif.frame_index = 0
