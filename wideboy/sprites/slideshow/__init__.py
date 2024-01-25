import logging
from enum import Enum
from pygame import Rect, Surface
from pygame.sprite import Sprite
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Transition(Enum):
    NONE = 0
    FADE = 1
    WIPE = 2
    BLEED = 3


class SlideshowSprite(Sprite):
    image: Surface
    image_buffer: Optional[Surface] = None
    rect: Rect
    transition: Optional[Transition] = None
    transition_out: bool = False
    transition_state: Dict[str, Any] = {}
    fade_speed: int = 4

    def __init__(self, surface: Surface) -> None:
        self.image = surface
        self.rect = self.image.get_rect()

    def set_next_image(self, surface: Surface) -> None:
        self.image_buffer = surface

    def swap(self, transition: Transition = Transition.NONE) -> None:
        if self.image_buffer is None:
            return
        # Start transition and set direction (fading down)
        self.transition = transition
        self.transition_out = True

    def update(self) -> None:
        if self.image_buffer is None:
            return
        # If no transition, just swap images
        if self.transition == Transition.NONE:
            self.image = self.image_buffer
            self.image_buffer = None
            self.transition = None
        elif self.transition == Transition.FADE:
            self._transition_fade()
        elif self.transition == Transition.WIPE:
            self._transition_wipe()
        elif self.transition == Transition.BLEED:
            self._transition_bleed()

    def reset_transition(self) -> None:
        self.transition = None
        self.transition_state = {}

    def _transition_fade(self) -> None:
        if self.image_buffer is None:
            return
        image_alpha = self.image.get_alpha() or 0
        # If fading down, decrease alpha. When alpha reaches 0, swap images
        if self.transition_out:
            if image_alpha > 0:
                image_alpha -= self.fade_speed
            else:
                image_alpha = 0
                self.transition_out = False
                self.image = self.image_buffer
        # If fading up, increase alpha. When alpha reaches 255, stop transition, and reset direction
        else:
            if image_alpha < 255:
                image_alpha += self.fade_speed
            else:
                image_alpha = 255
                self.transition_out = True
                self.reset_transition()
        # Set image alpha
        self.image.set_alpha(image_alpha)

    def _transition_wipe(self, speed: int = 4) -> None:
        if self.image_buffer is None:
            return
        self.transition_state["x"] = self.transition_state.get("x", 1)
        # Wipe out old image
        if self.transition_state["x"] < self.rect.width:
            self.transition_state["x"] += speed
            self.image.blit(
                self.image_buffer,
                (0, 0),
                (0, 0, self.transition_state["x"], self.rect.height),
            )
        # When wipe is complete, swap images and reset state
        else:
            self.image = self.image_buffer
            self.image_buffer = None
            self.reset_transition()

    def _transition_bleed(self, speed: int = 1) -> None:
        if self.image_buffer is None:
            return
        self.transition_state["y"] = self.transition_state.get("y", 0)
        # Wipe out old image
        if self.transition_state["y"] < self.rect.height:
            self.transition_state["y"] += speed
            self.image.blit(
                self.image_buffer,
                (0, 0),
                (0, 0, self.rect.width, self.transition_state["y"]),
            )
            self.image.blit(
                self.image_buffer,
                (0, self.transition_state["y"]),
                (
                    0,
                    self.rect.height - self.transition_state["y"],
                    self.rect.width,
                    self.transition_state["y"],
                ),
            )
        # When wipe is complete, swap images and reset state
        else:
            self.image = self.image_buffer
            self.image_buffer = None
            self.reset_transition()
