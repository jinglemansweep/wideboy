import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.utils.images import render_text
from wideboy.utils.pygame import EVENT_EPOCH_SECOND, EVENT_EPOCH_MINUTE
from wideboy.utils.state import StateStore
from wideboy.sprites import BaseSprite


logger = logging.getLogger("sprites.clock")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']


class ClockSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        color_bg: pygame.color.Color = (0, 0, 0),
        color_time: pygame.color.Color = (255, 255, 255, 255),
        color_date: pygame.color.Color = (255, 255, 0, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_time = color_time
        self.color_date = color_date
        self.font_date = "bitstreamverasansmono"
        self.font_time = "molot"
        self.render()

    def update(
        self,
        frame: str,
        delta: float,
        events: list[pygame.event.Event],
        state: StateStore,
    ) -> None:
        super().update(frame, delta, events, state)
        for event in events:
            if event.type == EVENT_EPOCH_MINUTE:
                self.render()

    def render(self) -> None:
        now = datetime.now()
        dow_str = now.strftime("%A")[:2]
        ddmm_str = now.strftime("%b%d").upper()
        hhmm_str = now.strftime("%H:%M")
        mm_str = now.strftime("%M")
        date_str = f"{ddmm_str}"
        self.image.fill(self.color_bg)
        date_sprite = render_text(
            date_str, self.font_date, 12, self.color_date, bold=True
        )
        date_pos = (90, 40)
        self.image.blit(date_sprite, date_pos)
        hhmm_sprite = render_text(hhmm_str, self.font_time, 48, self.color_time)
        time_pos = ((self.rect[2] - hhmm_sprite.get_rect()[2]) // 2, -10)
        self.image.blit(hhmm_sprite, time_pos)
        self.dirty = 1

    def poop(self) -> None:
        logger.info("POOP")
