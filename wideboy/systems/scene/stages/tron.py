import logging
from ecs_pattern import EntityManager
from typing import Tuple
from ....entities import (
    Cache,
    WidgetClockDate,
    WidgetClockTime,
    WidgetTronGrid,
    WidgetTileGrid,
)
from ..sprites import build_image_sprite
from . import Stage

logger = logging.getLogger(__name__)


class StageTron(Stage):
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
                WidgetTronGrid(
                    build_image_sprite(self.cache.surfaces["mode7_tron_grid"][0]),
                    x=0,
                    y=0,
                    z_order=5,
                    frames=self.cache.surfaces["mode7_tron_grid"],
                    frame_delay=10,
                ),  # type: ignore[call-arg]
            ]
        )

        for w in self.entities.get_by_class(
            WidgetClockDate,
            WidgetClockTime,
            WidgetTileGrid,
        ):
            w.fade_target_alpha = 255
