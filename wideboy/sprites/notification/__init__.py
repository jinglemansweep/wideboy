import logging
import pygame
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA
from typing import List, Optional
from wideboy.constants import EVENT_NOTIFICATION_RECEIVED
from wideboy.scenes.base import BaseScene
from wideboy.sprites.base import BaseSprite
from wideboy.sprites.image_helpers import render_text


logger = logging.getLogger("sprite.notification")


class NotificationSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        font_name: str = "fonts/bitstream-vera.ttf",
        font_size: int = 32,
        font_padding: int = 8,
        color_fg: Color = Color(0, 0, 0, 255),
        color_bg: Color = Color(255, 255, 255, 255),
        color_outline: Color = Color(0, 0, 0, 255),
        alpha: int = 255,
        timeout_frames: int = 300,
        fadeout_frames: int = 25,
    ) -> None:
        super().__init__(scene, rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.font_name = font_name
        self.font_size = font_size
        self.font_padding = font_padding
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.alpha = alpha
        self.timeout_frames = timeout_frames
        self.fadeout_frames = fadeout_frames
        self.message: Optional[str] = None
        self.timeout = 0
        self.notifications: List[str] = []
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        self.handle_events(events)
        if self.timeout > 0:
            self.timeout -= 1
            self.render()
        else:
            if len(self.notifications) > 0:
                self.message = self.notifications.pop(0)
                self.timeout = self.timeout_frames
            else:
                self.message = None

    def handle_events(self, events: list[Event]) -> None:
        for event in events:
            if event.type == EVENT_NOTIFICATION_RECEIVED:
                logger.debug(f"notification: message={event.payload}")
                self.notifications.append(event.payload)

    def render(self) -> None:
        self.image.fill(self.color_bg if self.timeout > 0 else Color(0, 0, 0, 0))
        if not self.message:
            self.surface_text = None
        else:
            if self.surface_text is None:
                self.surface_text = render_text(
                    f"{self.message}",
                    self.font_name,
                    self.font_size,
                    self.color_fg,
                    color_outline=self.color_outline,
                )

            self.image.blit(
                self.surface_text,
                (
                    (self.rect.width - self.surface_text.get_width()) / 2,
                    self.font_padding,
                ),
            )
            progress_width = (self.timeout_frames - self.timeout) / self.timeout_frames
            pygame.draw.rect(
                self.image,
                Color(0, 255, 0),
                Rect(
                    0,
                    self.rect.height - 2,
                    self.rect.width * progress_width,
                    2,
                ),
            )
            pygame.draw.rect(
                self.image,
                Color(0, 255, 0),
                Rect(
                    self.rect.width - self.rect.width * progress_width,
                    0,
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
