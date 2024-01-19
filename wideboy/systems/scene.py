import logging
from ecs_pattern import EntityManager, System
from pygame.event import get as get_events
from pygame.display import Info as DisplayInfo
from ..consts import EVENT_CLOCK_NEW_SECOND, EVENT_HASS_ENTITY_UPDATE
from ..entities import (
    AppState,
    WidgetClock,
    WidgetTest,
    WidgetTileGrid,
)
from ..sprites.common import clock_sprite, test_sprite
from ..sprites.tile_grid import build_tile_grid_sprite
from ..sprites.tile_grid.tiles import CELLS

logger = logging.getLogger(__name__)


class SysScene(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.display_info = DisplayInfo()

    def start(self):
        logger.info("Scene system starting...")
        self.entities.init()
        app_state = next(self.entities.get_by_class(AppState))
        self.entities.add(
            WidgetClock(clock_sprite(""), 0, 0),
            WidgetTest(test_sprite(), 1, 1, 1, 1),
            WidgetTileGrid(build_tile_grid_sprite(CELLS, app_state.hass_state), 20, 50),
        )

        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_tilegrid.speed_x, widget_tilegrid.speed_y = -1, -1

    def update(self) -> None:
        widget_clock = next(self.entities.get_by_class(WidgetClock))
        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_test = next(self.entities.get_by_class(WidgetTest))

        for event in get_events((EVENT_CLOCK_NEW_SECOND, EVENT_HASS_ENTITY_UPDATE)):
            if event.type == EVENT_CLOCK_NEW_SECOND:
                widget_clock.sprite = clock_sprite(event.now.strftime("%H:%M:%S"))
            if event.type == EVENT_HASS_ENTITY_UPDATE:
                widget_tilegrid.sprite.update(event.entity_id)

        if widget_tilegrid.x <= 0 or widget_tilegrid.x > self.display_info.current_w:
            widget_tilegrid.speed_x = -widget_tilegrid.speed_x
        elif widget_tilegrid.y <= 0 or widget_tilegrid.y > self.display_info.current_h:
            widget_tilegrid.speed_y = -widget_tilegrid.speed_y

        if widget_test.x <= 0 or widget_test.x > self.display_info.current_w:
            widget_test.speed_x = -widget_test.speed_x
        elif widget_test.y <= 0 or widget_test.y > self.display_info.current_h:
            widget_test.speed_y = -widget_test.speed_y
