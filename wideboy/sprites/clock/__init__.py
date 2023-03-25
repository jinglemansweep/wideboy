import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.sprites.images import render_text
from wideboy.utils.pygame import EVENT_EPOCH_SECOND
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprites.clock")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']


class ClockSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0, 255),
        color_time: pygame.color.Color = (0, 255, 0, 255),
        color_date: pygame.color.Color = (255, 255, 255, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_time = color_time
        self.color_date = color_date
        self.font_date = "fonts/digital.ttf"
        self.font_time = "fonts/digital.ttf"
        self.render()

    def update(
        self, frame: str, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND:
                self.render()

    def render(self) -> None:
        now = datetime.now()
        dow_str = now.strftime("%A")[:3]
        ddmm_str = now.strftime("%d %b")
        date_str = f"{dow_str} {ddmm_str}"
        self.image.fill(self.color_bg)
        hh_str = now.strftime("%H")
        mm_str = now.strftime("%M")
        hhmm_str = f"{hh_str}:{mm_str}" if now.second % 2 == 0 else f"{hh_str} {mm_str}"
        hhmm_sprite = render_text(hhmm_str, self.font_time, 50, self.color_time)
        time_pos = ((self.rect[2] - hhmm_sprite.get_rect()[2]) // 2, -2)
        self.image.blit(hhmm_sprite, time_pos)
        date_sprite = render_text(date_str, self.font_date, 24, self.color_date)
        date_pos = ((self.rect[2] - date_sprite.get_rect()[2]) // 2, 38)
        self.image.blit(date_sprite, date_pos)
        self.dirty = 1
