import logging
from ecs_pattern import EntityManager
from typing import Tuple
from ....entities import (
    Cache,
    WidgetClockDate,
    WidgetClockTime,
    WidgetVinyl,
    WidgetTileGrid,
)
from ..sprites import build_image_sprite
from . import Stage

logger = logging.getLogger(__name__)


class StageVinyl(Stage):
    image_count: int

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
                WidgetVinyl(
                    build_image_sprite(self.cache.surfaces["mode7_vinyl"][0]),
                    x=-100,
                    y=0,
                    z_order=5,
                    frames=self.cache.surfaces["mode7_vinyl"],
                    frame_delay=1,
                ),  # type: ignore[call-arg]
                WidgetVinyl(
                    build_image_sprite(self.cache.surfaces["mode7_vinyl_serato"][0]),
                    x=420,
                    y=24,
                    z_order=5,
                    frames=self.cache.surfaces["mode7_vinyl_serato"],
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
