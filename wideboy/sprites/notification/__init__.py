import logging
import pygame
from pygame import SRCALPHA
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_text
from wideboy.state import STATE

logger = logging.getLogger("sprite.notification")


class NotificationSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 32,
        color_fg: pygame.color.Color = (0, 0, 0, 255),
        color_bg: pygame.color.Color = (255, 255, 255, 255),
        color_outline: pygame.color.Color = (0, 0, 0, 255),
        alpha: int = 255,
        timeout_frames: int = 300,
        fadeout_frames: int = 25,
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.font_name = font_name
        self.font_size = font_size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.alpha = alpha
        self.timeout_frames = timeout_frames
        self.fadeout_frames = fadeout_frames
        self.message = None
        self.timeout = 0
        self.render()

    def update(
        self,
        frame: str,
        clock: pygame.time.Clock,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        if self.timeout > 0:
            self.timeout -= 1
        else:
            if len(STATE.notifications) > 0:
                self.message = STATE.notifications.pop(0)
                self.timeout = self.timeout_frames
            else:
                self.message = None
        self.render()

    def render(self) -> None:
        self.image.fill(self.color_bg if self.timeout > 0 else (0, 0, 0, 0))
        if self.message:
            text_surface = render_text(
                f"{self.message}",
                self.font_name,
                self.font_size,
                self.color_fg,
                color_outline=self.color_outline,
            )

            self.image.blit(
                text_surface, ((self.rect.width - text_surface.get_width()) / 2, 8)
            )
            progress_width = (self.timeout_frames - self.timeout) / self.timeout_frames
            pygame.draw.rect(
                self.image,
                (0, 255, 0),
                (
                    0,
                    self.rect.height - 2,
                    self.rect.width * progress_width,
                    2,
                ),
            )
            self.image.set_alpha(
                self.timeout * (255 // self.fadeout_frames)
                if self.timeout < self.fadeout_frames
                else 255
            )

        self.dirty = 1
