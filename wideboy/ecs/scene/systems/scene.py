from ecs_pattern import EntityManager, System
from pygame.event import Event, get as get_events, post as post_event
from pygame.display import Info as DisplayInfo
from ..consts import EVENT_CLOCK_NEW_SECOND, EVENT_DEBUG_LOG, EVENT_HASS_ENTITY_UPDATE
from ..entities import (
    AppState,
    WidgetClock,
    WidgetTest,
    WidgetTileGrid,
)
from ..sprites import clock_sprite, test_sprite, tilegrid_sprite

from ....scenes.default.tiles import CELLS


class SysScene(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.display_info = DisplayInfo()

    def start(self):
        self.entities.init()
        app_state = next(self.entities.get_by_class(AppState))
        self.entities.add(
            WidgetClock(clock_sprite(""), 0, 0),
            WidgetTest(test_sprite(), 100, 100, 1, 1),
            WidgetTileGrid(tilegrid_sprite(CELLS, app_state.hass_state), 20, 50),
        )

    def update(self):
        for event in get_events((EVENT_CLOCK_NEW_SECOND, EVENT_HASS_ENTITY_UPDATE)):
            if event.type == EVENT_CLOCK_NEW_SECOND:
                post_event(
                    Event(
                        EVENT_DEBUG_LOG,
                        dict(msg=f"Clock: {event.now.strftime('%H:%M:%S')}"),
                    ),
                )
                clock = next(self.entities.get_by_class(WidgetClock))
                clock.sprite = clock_sprite(event.now.strftime("%H:%M:%S"))
            if event.type == EVENT_HASS_ENTITY_UPDATE:
                widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
                widget_tilegrid.sprite.update(event.entity_id)

        widget_tilegrid = next(self.entities.get_by_class(WidgetTileGrid))
        widget_tilegrid.sprite.update()

        test_entity = next(self.entities.get_by_class(WidgetTest))
        if test_entity.x < 0:
            test_entity.speed_x = -test_entity.speed_x
        if test_entity.x > self.display_info.current_w:
            test_entity.speed_x = -test_entity.speed_x
        if test_entity.y < 0:
            test_entity.speed_y = -test_entity.speed_y
        if test_entity.y > self.display_info.current_h:
            test_entity.speed_y = -test_entity.speed_y
