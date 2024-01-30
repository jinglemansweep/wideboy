import logging
import random
from ecs_pattern import EntityManager
from typing import Tuple
from ....entities import (
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
        self.cache = next(self.entities.get_by_class(Cache))

        cache_key = random.choice(IMAGE_CACHE_KEYS)

        self.stage_entities.append(
            WidgetAnimatedGif(
                build_image_sprite(self.cache.surfaces[cache_key][0]),
                x=0,
                y=0,
                z_order=5,
                frames=self.cache.surfaces[cache_key],
                frame_delay=2,
            ),  # type: ignore[call-arg]
        )

        for w in self.entities.get_by_class(
            WidgetClockDate,
            WidgetClockTime,
            WidgetTileGrid,
        ):
            w.fade_target_alpha = 255
