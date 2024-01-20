import logging
from ecs_pattern import EntityManager, System
from pygame.display import Info as DisplayInfo
from ..consts import EventTypes
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
        self.app_state = next(self.entities.get_by_class(AppState))
        self.entities.add(
            WidgetClock(clock_sprite(""), 0, 0),
            WidgetTest(test_sprite(), 1, 1, 1, 2),
            WidgetTileGrid(
                build_tile_grid_sprite(CELLS, self.app_state.hass_state), 512, 0
            ),
        )

    def update(self) -> None:
        # logger.debug(f"sys.scene.update: events={len(self.app_state.events)}")
        widget_clock = next(self.entities.get_by_class(WidgetClock))
        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_test = next(self.entities.get_by_class(WidgetTest))

        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                widget_clock.sprite = clock_sprite(
                    event_payload["now"].strftime("%H:%M:%S")
                )
            elif event_type == EventTypes.EVENT_HASS_ENTITY_UPDATE:
                widget_tilegrid.sprite.update(event_payload["entity_id"])

        widget_tilegrid.sprite.update()

        if widget_test.x <= 0 or widget_test.x > self.display_info.current_w:
            widget_test.speed_x = -widget_test.speed_x
        elif (
            widget_test.y <= 0
            or widget_test.y
            > self.display_info.current_h - widget_test.sprite.rect.height
        ):
            widget_test.speed_y = -widget_test.speed_y
