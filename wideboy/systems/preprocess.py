import logging
import random
import time
from ecs_pattern import EntityManager, System
from functools import partial
from typing import List, Tuple
from ..entities import AppState, Cache, WidgetSysMessage
from ..sprites.text import build_system_message_sprite

logger = logging.getLogger(__name__)

# Preprocessing Functions


def _preprocess_text(cache: Cache, key: str, text: str):
    logger.debug(f"_preprocess_text: key={key} text={text}")
    sprite = build_system_message_sprite(text)
    if key not in cache.surfaces:
        cache.surfaces[key] = []
    cache.surfaces[key].append(sprite.image)


class SysPreprocess(System):
    entities: EntityManager
    app_state: AppState
    cache: Cache
    queue: List[Tuple] = []
    step_index: int = 0

    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Preprocessing system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))
        self.cache = next(self.entities.get_by_class(Cache))
        for i in range(10):
            self.queue.append((_preprocess_text, (self.cache, "test", f"Step {i}")))

    def update(self) -> None:
        if not self.app_state.booting:
            # logger.debug(f"sys.preprocess.update: booting={self.app_state.booting}")
            return

        if not self.cache:
            return

        if len(self.queue):
            task = self.queue.pop(0)
            self._progress(f"Getting ready {('.' * self.step_index)}")
            partial(task[0], *task[1])()
            sleep_time = random.randrange(10, 200) * 1000.0
            time.sleep(sleep_time / 1000000.0)
            self.step_index += 1
        else:
            self.app_state.booting = False
            self._progress(visible=False)

    def _progress(self, message: str = "", visible: bool = True) -> None:
        widget_message = next(self.entities.get_by_class(WidgetSysMessage))
        if widget_message is not None:
            widget_message.hidden = not visible
            widget_message.sprite = build_system_message_sprite(message)
