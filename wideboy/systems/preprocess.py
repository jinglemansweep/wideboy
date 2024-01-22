import logging
import random
import time
from ecs_pattern import EntityManager, System
from functools import partial
from pygame.image import load as pygame_image_load
from typing import Callable, List, Tuple
from ..entities import AppState, Cache, WidgetSysMessage
from ..sprites.text import build_system_message_sprite

logger = logging.getLogger(__name__)

# Preprocessing Functions


def _preprocess_load_image(cache: Cache, key: str, path: str):
    logger.debug(f"_preprocess_load_image: key={key} path={path}")
    if key not in cache.surfaces:
        cache.surfaces[key] = []
    cache.surfaces[key].append(pygame_image_load(path))


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
    queue: List[Tuple[Callable, Tuple]] = []
    queue_length: int = 0
    step_index: int = 0

    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Preprocessing system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))
        print(self.app_state.config.paths.images_sprites)
        self.cache = next(self.entities.get_by_class(Cache))
        for i in range(4, 8):
            self.queue.append(
                (
                    _preprocess_load_image,
                    (
                        self.cache,
                        "dino",
                        f"{self.app_state.config.paths.images_sprites}/dino/image_{i}.png",
                    ),
                ),
            )
        # for i in range(20):
        #     self.queue.append((_preprocess_text, (self.cache, "test", f"Step {i}")))
        self.queue_length = len(self.queue)

    def update(self) -> None:
        if not self.app_state.booting:
            # logger.debug(f"sys.preprocess.update: booting={self.app_state.booting}")
            return

        if not self.cache:
            return

        if len(self.queue):
            task = self.queue.pop(0)
            percent = int((self.step_index / self.queue_length) * 100)
            self._progress(f"Getting ready... {percent}%")
            partial(task[0], *task[1])()
            sleep_time = random.randrange(10, 50) * 1000.0
            time.sleep(sleep_time / 1000000.0)
            self.step_index += 1
        else:
            self.app_state.booting = False
            self._progress(visible=False)

    def _progress(self, message: str = "", visible: bool = True) -> None:
        widget_message = next(self.entities.get_by_class(WidgetSysMessage))
        if widget_message is not None:
            widget_message.fade_target_alpha = 255 if visible else 0
            widget_message.sprite = build_system_message_sprite(message)
