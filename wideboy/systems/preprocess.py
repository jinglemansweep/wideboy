import logging
import random
import time
from ecs_pattern import EntityManager, System
from typing import List
from ..entities import AppState, WidgetSysMessage
from ..sprites.text import build_system_message_sprite

logger = logging.getLogger(__name__)


class SysPreprocess(System):
    entities: EntityManager
    app_state: AppState
    queue: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def __init__(
        self,
        entities: EntityManager,
    ) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Preprocessing system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        if not self.app_state.booting:
            logger.debug(f"sys.preprocess.update: booting={self.app_state.booting}")
            return

        if len(self.queue):
            result = self.queue.pop(0)
            self._progress(f"Getting ready {('.' * result)}")
            sleep_time = random.randrange(100, 1000) * 1000.0
            logger.debug(
                f"sys.preprocess.update: queue_item={result} sleep_time={sleep_time}"
            )
            time.sleep(sleep_time / 1000000.0)
        else:
            self.app_state.booting = False
            self._progress(visible=False)

    def _progress(self, message: str = "", visible: bool = True) -> None:
        widget_message = next(self.entities.get_by_class(WidgetSysMessage))
        if widget_message is not None:
            widget_message.hidden = not visible
            widget_message.sprite = build_system_message_sprite(message)
