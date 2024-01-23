import logging
import random
from ecs_pattern import EntityManager
from typing import Tuple
from ....entities import (
    Cache,
    WidgetClockDate,
    WidgetImage,
    WidgetTileGrid,
)
from ..sprites import build_image_sprite
from . import Stage

logger = logging.getLogger(__name__)


class StageNight(Stage):
    image_count: int

    def __init__(
        self,
        entities: EntityManager,
        display_size: Tuple[int, int],
        image_count: int = 20,
    ) -> None:
        super().__init__(entities)
        self.display_size = display_size
        self.image_count = image_count
        self.setup()

    def setup(self) -> None:
        cache = next(self.entities.get_by_class(Cache))
        for i in range(self.image_count):
            self.stage_entities.append(
                WidgetImage(
                    build_image_sprite(cache.surfaces["duck_pixel"][0]),
                    x=random.randint(0, self.display_size[0] - 32),
                    y=random.randint(0, self.display_size[1] - 32),
                    alpha=random.randrange(32, 128),
                    speed_x=random.choice([-1, 1]),
                    speed_y=random.choice([-1, 1]),
                    bound_rect=(0, 0, self.display_size[0], self.display_size[1]),
                    bound_size=(32, 32),
                    bound_mode="loop",
                ),  # type: ignore[call-arg]
            )
        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_tilegrid.fade_target_alpha = 128
        widget_clock_date = next(self.entities.get_by_class(WidgetClockDate))
        widget_clock_date.fade_target_alpha = 0
