import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.utils.images import render_text
from wideboy.utils.pygame import EVENT_EPOCH_MINUTE
from wideboy.utils.state import StateStore
from wideboy.sprites import BaseSprite


logger = logging.getLogger("sprites.clock")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']


class ClockSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        state: StateStore,
        color_bg: pygame.color.Color = (0, 0, 0, 255),
        color_time: pygame.color.Color = (0, 255, 0, 255),
        color_date: pygame.color.Color = (255, 255, 255, 255),
    ) -> None:
        super().__init__(rect, state)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_time = color_time
        self.color_date = color_date
        self.font_date = "fonts/molot.otf"
        self.font_time = "fonts/digital.ttf"
        self.render()

    def update(
        self, frame: str, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                self.render()

    def render(self) -> None:
        now = datetime.now()
        dow_str = now.strftime("%A")[:3]
        ddmm_str = now.strftime("%d %b")
        date_str = f"{dow_str} {ddmm_str}"
        self.image.fill(self.color_bg)
        hhmm_str = now.strftime("%H:%M")
        hhmm_sprite = render_text(hhmm_str, self.font_time, 50, self.color_time)
        time_pos = (((self.rect[2] - hhmm_sprite.get_rect()[2]) // 2) + 2, 0)
        self.image.blit(hhmm_sprite, time_pos)
        date_sprite = render_text(date_str, self.font_date, 18, self.color_date)
        date_pos = ((self.rect[2] - date_sprite.get_rect()[2]) // 2, 38)
        self.image.blit(date_sprite, date_pos)
        self.dirty = 1
