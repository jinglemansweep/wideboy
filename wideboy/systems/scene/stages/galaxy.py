import logging
from ecs_pattern import EntityManager
from typing import Tuple
from ....entities import (
    Cache,
    WidgetClockDate,
    WidgetClockTime,
    WidgetGalaxy,
    WidgetTileGrid,
)
from ..sprites import build_image_sprite
from . import Stage

logger = logging.getLogger(__name__)


class StageGalaxy(Stage):
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

        self.stage_entities.extend(
            [
                WidgetGalaxy(
                    build_image_sprite(self.cache.surfaces["mode7_milky_way"][0]),
                    x=0,
                    y=0,
                    z_order=5,
                    frames=self.cache.surfaces["mode7_milky_way"],
                    frame_delay=2,
                ),  # type: ignore[call-arg]
            ]
        )

        for w in self.entities.get_by_class(
            WidgetClockDate,
            WidgetClockTime,
            WidgetTileGrid,
        ):
            w.fade_target_alpha = 255
