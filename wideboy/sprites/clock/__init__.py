import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.sprites.image_helpers import render_text
from wideboy.constants import EVENT_EPOCH_SECOND
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.clock")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']


class ClockSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 0),
        color_time: pygame.color.Color = (255, 0, 255, 255),
        color_date: pygame.color.Color = (192, 192, 255, 255),
        font_date: str = "fonts/huggable.ttf",
        font_time: str = "fonts/huggable.ttf",
        font_time_size: int = 50,
        font_date_size: int = 20,
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_time = color_time
        self.color_date = color_date
        self.font_date = font_date
        self.font_date_size = font_date_size
        self.font_time = font_time
        self.font_time_size = font_time_size
        self.render()

    def update(
        self,
        frame: str,
        clock: pygame.time.Clock,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND:
                self.render()

    def render(self) -> None:
        now = datetime.now()
        dow_str = now.strftime("%A")[:3]
        ddmm_str = now.strftime("%d %b")
        date_str = f"{dow_str} {ddmm_str}".upper()
        self.image.fill(self.color_bg)
        hh_str = now.strftime("%H")
        mm_str = now.strftime("%M")
        hhmm_str = f"{hh_str}:{mm_str}"
        hhmm_str = "12:34"
        hhmm_offset = (0, -6)
        hhmm_sprite = render_text(
            hhmm_str, self.font_time, self.font_time_size, self.color_time
        )
        print(self.rect.width, hhmm_sprite.get_rect().width)
        self.image.blit(
            hhmm_sprite,
            (
                (self.rect.width / 2) - (hhmm_sprite.get_rect().width / 2),
                hhmm_offset[1],
            ),
        )
        date_sprite = render_text(
            date_str, self.font_date, self.font_date_size, self.color_date
        )
        date_pos = (((self.rect.width / 2) - date_sprite.get_rect().width / 2), 30)
        self.image.blit(date_sprite, date_pos)
        self.dirty = 1
