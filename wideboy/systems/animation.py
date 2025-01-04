import logging
from ecs_pattern import EntityManager, System, entity

from pygame.transform import flip as pygame_transform_flip
from ..components import (
    ComponentAlpha,
    ComponentBound,
    ComponentFade,
    ComponentFrame,
    ComponentMotion,
    ComponentTarget,
    ComponentVisible,
)

logger = logging.getLogger(__name__)


class SysAnimation(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Animation system starting...")

    def update(self) -> None:
        self._update_fade()
        self._update_alpha()
        self._update_target()
        self._update_bound()
        self._update_frame()
        self._update_motion()

    def _update_fade(self):
        # Handle fade animation
        for e in self.entities.get_with_component(ComponentFade, ComponentVisible):
            # If no fade target, skip
            if e.fade_target_alpha is None:
                continue
            # If current alpha is less than target, increase alpha
            if e.alpha < e.fade_target_alpha:
                # If the difference between current and target is less than the speed, set to target
                if abs(e.alpha - e.fade_target_alpha) < e.fade_speed:
                    e.alpha = e.fade_target_alpha
                else:
                    e.alpha += e.fade_speed
            # If current alpha is greater than target, decrease alpha
            if e.alpha > e.fade_target_alpha:
                # If the difference between current and target is less than the speed, set to target
                if abs(e.alpha - e.fade_target_alpha) < e.fade_speed:
                    e.alpha = e.fade_target_alpha
                else:
                    e.alpha -= e.fade_speed
            # If current alpha is equal to target, set target to None
            if e.alpha == e.fade_target_alpha:
                e.fade_target_alpha = None

    def _update_target(self):
        # Set speed to move towards target
        for e in self.entities.get_with_component(
            ComponentTarget, ComponentMotion, ComponentVisible
        ):
            # If X target set, move towards it
            if e.target_x is not None:
                # If current X is less than target, move right
                if e.x < e.target_x:
                    e.speed_x = 1
                # If current X is greater than target, move left
                elif e.x > e.target_x:
                    e.speed_x = -1
                # If current X is equal to target, set target to None
                else:
                    e.target_x = None
                    e.speed_x = 0
            # If Y target set, move towards it
            if e.target_y is not None:
                # If current Y is less than target, move down
                if e.y < e.target_y:
                    e.speed_y = 1
                # If current Y is greater than target, move up
                elif e.y > e.target_y:
                    e.speed_y = -1
                # If current Y is equal to target, set target to None
                else:
                    e.target_y = None
                    e.speed_y = 0

    def _update_bound(self):
        for e in self.entities.get_with_component(
            ComponentBound, ComponentMotion, ComponentVisible
        ):
            # If no bound rect or size, skip
            if e.bound_rect is None or e.bound_size is None:
                continue

            # Call bound update function based on mode
            if e.bound_mode == "bounce":
                self._update_bound_bounce(e)
            elif e.bound_mode == "loop":
                self._update_bound_loop(e)

    def _update_bound_bounce(self, e: entity):
        # If entity is outside of X bounds, reverse speed
        if e.x < e.bound_rect[0] or e.x > e.bound_rect[2] - e.bound_size[0]:
            e.speed_x = -e.speed_x

        # If entity is outside of Y bounds, reverse speed
        if e.y < e.bound_rect[1] or e.y > e.bound_rect[3] - e.bound_size[1]:
            e.speed_y = -e.speed_y

    def _update_bound_loop(self, e: entity):
        # If entity is outside of X bounds, loop to other side
        if e.x < e.bound_rect[0] - e.bound_size[0]:
            e.x = e.bound_rect[2]
        elif e.x > e.bound_rect[2]:
            e.x = e.bound_rect[0] - e.bound_size[0]

        # If entity is outside of Y bounds, loop to other side
        if e.y < e.bound_rect[1] - e.bound_size[1]:
            e.y = e.bound_rect[3]
        elif e.y > e.bound_rect[3]:
            e.y = e.bound_rect[1] - e.bound_size[1]

    def _update_frame(self):
        # Handle frame animation
        for e in self.entities.get_with_component(ComponentFrame, ComponentVisible):
            # If zero or one frame, skip
            if len(e.frames) <= 1:
                continue
            # Only update frame every "frame_delay" frames
            if e.scene_frame % e.frame_delay == 0:
                # Set sprite to frame surface at index
                e.sprite.image = e.frames[e.frame_index]
                # Advance or reverse frame index
                e.frame_index += e.frame_direction
                if e.frame_index >= len(e.frames):
                    e.frame_index = 0
                elif e.frame_index < 0:
                    e.frame_index = len(e.frames) - 1
            # Increment scene frame
            e.scene_frame += 1

    def _update_motion(self):
        # Move entity according to speed and set direction
        for e in self.entities.get_with_component(ComponentMotion, ComponentVisible):
            # Increase or decrease X and Y by speed
            e.x += e.speed_x
            e.y += e.speed_y
            # Set direction based on speed
            e.direction_x = 1 if e.speed_x > 0 else -1 if e.speed_x < 0 else 0
            e.direction_y = 1 if e.speed_y > 0 else -1 if e.speed_y < 0 else 0

        # Flip sprite if moving left
        for e in self.entities.get_with_component(ComponentFrame, ComponentMotion):
            # If moving left, flip sprite
            if e.direction_x < 0:
                e.sprite.image = pygame_transform_flip(
                    e.frames[e.frame_index], True, False
                )

    def _update_alpha(self):
        for e in self.entities.get_with_component(ComponentAlpha):
            # Set alpha of sprite image
            e.sprite.image.set_alpha(e.alpha)
