import logging
import random
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

from ..sprites.text import TextSprite
from ..sprites.tile_grid import build_tile_grid_sprite
from ..sprites.tile_grid.tiles import CELLS

logger = logging.getLogger(__name__)


def random_color():
    return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


CLOCK_WIDTH = 110


def build_time_sprite(text: str, color_fg: Color = Color(255, 255, 0, 255)):
    return TextSprite(text, font_size=36, color_fg=color_fg)


def build_date_sprite(text: str, color_fg: Color = Color(255, 255, 255, 255)):
    return TextSprite(
        text,
        font_size=17,
        color_fg=color_fg,
    )


class SysScene(System):
    first_run = True

    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.display_info = DisplayInfo()

    def start(self):
        logger.info("Scene system starting...")

        self.entities.init()
        self.app_state = next(self.entities.get_by_class(AppState))

        for i in range(50):
            self.entities.add(
                WidgetTest(
                    test_sprite(color=random_color()),
                    random.randint(0, self.display_info.current_w - 32),
                    random.randint(0, self.display_info.current_h - 32),
                    random.choice([-2, -1, 1, 2]),
                    random.choice([-1, 1]),
                ),
            )

        clock_x = self.display_info.current_w - CLOCK_WIDTH
        clock_y = 1
        self.entities.add(
            WidgetClockTime(
                build_time_sprite(""),
                clock_x,
                clock_y,
            ),
            WidgetClockDate(
                build_date_sprite(""),
                clock_x + 3,
                clock_y + 30,
            ),
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

        time_fmt = "%H:%M" if app_state.clock_24_hour else "%i:%M %p"
        date_fmt = "%a %d %b"

        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                widget_clock_time.sprite = build_time_sprite(
                    app_state.time_now.strftime(time_fmt)
                )
            if event_type == EventTypes.EVENT_CLOCK_NEW_MINUTE or self.first_run:
                widget_clock_date.sprite = build_date_sprite(
                    app_state.time_now.strftime(date_fmt)
                )
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

        self.first_run = False
