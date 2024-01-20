import logging
import random
from datetime import datetime
from ecs_pattern import EntityManager, System
from pygame import Color
from pygame.display import Info as DisplayInfo
from ..components import ComMotion
from ..consts import EventTypes
from ..entities import (
    AppState,
    WidgetClockDate,
    WidgetClockTime,
    WidgetTest,
    WidgetTileGrid,
)
from ..sprites.common import test_sprite
from ..sprites.clock import (
    build_clock_date_sprite,
    build_clock_time_sprite,
    CLOCK_WIDTH,
)
from ..sprites.tile_grid import build_tile_grid_sprite
from ..sprites.tile_grid.tiles import CELLS

logger = logging.getLogger(__name__)


def random_color():
    return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


class SysScene(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.display_info = DisplayInfo()

    def start(self):
        logger.info("Scene system starting...")
        now = datetime.now()
        self.entities.init()
        self.app_state = next(self.entities.get_by_class(AppState))

        for i in range(10):
            self.entities.add(
                WidgetTest(
                    test_sprite(color=random_color()),
                    (i + 1) * 32,
                    random.randint(0, self.display_info.current_h - 32),
                    random.choice([-1, 1]),
                    random.choice([-1, 1]),
                ),
            )

        clock_x = self.display_info.current_w - CLOCK_WIDTH
        clock_y = 1
        self.entities.add(
            WidgetClockTime(
                build_clock_time_sprite(now, hours_24=self.app_state.clock_24_hour),
                clock_x,
                clock_y,
            ),
            WidgetClockDate(build_clock_date_sprite(now), clock_x, clock_y + 30),
            WidgetTileGrid(
                build_tile_grid_sprite(CELLS, self.app_state.hass_state),
                256,
                0,
            ),
        )

    def update(self) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        # logger.debug(f"sys.scene.update: events={len(self.app_state.events)}")
        widget_clock_date = next(self.entities.get_by_class(WidgetClockDate))
        widget_clock_time = next(self.entities.get_by_class(WidgetClockTime))
        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))

        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                widget_clock_time.sprite = build_clock_time_sprite(
                    event_payload["now"], app_state.clock_24_hour
                )
            if event_type == EventTypes.EVENT_CLOCK_NEW_MINUTE:
                widget_clock_date.sprite = build_clock_date_sprite(event_payload["now"])
            if event_type == EventTypes.EVENT_HASS_ENTITY_UPDATE:
                widget_tilegrid.sprite.update(event_payload["entity_id"])

        widget_tilegrid.x = (
            self.display_info.current_w
            - CLOCK_WIDTH
            - widget_tilegrid.sprite.rect.width
        )
        widget_tilegrid.sprite.update()

        for widget in self.entities.get_with_component(ComMotion):
            if (
                widget.x < 0
                or widget.x > self.display_info.current_w - widget.sprite.rect.width
            ):
                widget.speed_x = -widget.speed_x
            if (
                widget.y < 0
                or widget.y > self.display_info.current_h - widget.sprite.rect.height
            ):
                widget.speed_y = -widget.speed_y
