import logging
from ecs_pattern import EntityManager, System
from ..components import ComBound, ComFade, ComMotion, ComTarget, ComVisible

logger = logging.getLogger(__name__)


class SysAnimation(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Movement system starting...")

    def update(self) -> None:
        self._update_fade()
        self._update_targeting()
        self._update_bounds()
        self._update_core()

    def _update_fade(self):
        for e in self.entities.get_with_component(ComFade, ComVisible):
            if e.fade_target_alpha is None or e.alpha == e.fade_target_alpha:
                continue
            if e.alpha < e.fade_target_alpha:
                e.alpha += e.fade_speed
            elif e.alpha > e.fade_target_alpha:
                e.alpha -= e.fade_speed

    def _update_bounds(self):
        for e in self.entities.get_with_component(ComBound, ComMotion, ComVisible):
            if e.bound_rect is None or e.bound_size is None:
                continue

            if e.x < e.bound_rect[0] or e.x > e.bound_rect[2] - e.bound_size[0]:
                e.speed_x = -e.speed_x

            if e.y < e.bound_rect[1] or e.y > e.bound_rect[3] - e.bound_size[1]:
                e.speed_y = -e.speed_y

    def _update_targeting(self):
        for e in self.entities.get_with_component(ComTarget, ComMotion, ComVisible):
            # X Axis
            if e.target_x is not None:
                if e.x < e.target_x:
                    e.speed_x = 1
                elif e.x > e.target_x:
                    e.speed_x = -1
                else:
                    e.target_x = None
                    e.speed_x = 0
            # Y Axis
            if e.target_y is not None:
                if e.y < e.target_y:
                    e.speed_y = 1
                elif e.y > e.target_y:
                    e.speed_y = -1
                else:
                    e.target_y = None
                    e.speed_y = 0

    def _update_core(self):
        for e in self.entities.get_with_component(ComMotion, ComVisible):
            e.x += e.speed_x
            e.y += e.speed_y
            e.sprite.image.set_alpha(e.alpha)
