import logging
from pygame import Rect, Surface
from pygame.sprite import Sprite
from typing import Optional

logger = logging.getLogger(__name__)


class SlideshowSprite(Sprite):
    image: Surface
    image_buffer: Optional[Surface] = None
    rect: Rect
    transitioning: bool = False
    fade_speed: int = 4
    fade_down: bool = False

    def __init__(self, surface: Surface) -> None:
        self.image = surface
        self.rect = self.image.get_rect()

    def set_next_image(self, surface: Surface) -> None:
        self.image_buffer = surface

    def swap(self) -> None:
        if self.image_buffer is None:
            return
        # Start transition and set direction (fading down)
        self.transitioning = True
        self.fade_down = True

    def update(self) -> None:
        if not self.transitioning or self.image_buffer is None:
            return
        image_alpha = self.image.get_alpha() or 0
        # If fading down, decrease alpha. When alpha reaches 0, swap images
        if self.fade_down:
            if image_alpha > 0:
                image_alpha -= self.fade_speed
            else:
                image_alpha = 0
                self.fade_down = False
                self.image = self.image_buffer
        # If fading up, increase alpha. When alpha reaches 255, stop transition, and reset direction
        else:
            if image_alpha < 255:
                image_alpha += self.fade_speed
            else:
                image_alpha = 255
                self.fade_down = True
                self.transitioning = False
        # Set image alpha
        self.image.set_alpha(image_alpha)
