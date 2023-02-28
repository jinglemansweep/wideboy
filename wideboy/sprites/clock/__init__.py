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
        color_date: pygame.color.Color = (255, 0, 255, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.color_bg = color_bg
        self.color_time = color_time
        self.color_date = color_date
        self.font_date = "bitstreamverasansmono"
        self.font_time = "bitstreamverasansmono"
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
        ddmm_str = now.strftime("%d/%m")
        hh_str = now.strftime("%H")
        mm_str = now.strftime("%M")
        date_str = f"{dow_str} {ddmm_str}"
        self.image.fill(self.color_bg)
        date_sprite = render_text(date_str, self.font_date, 12, self.color_date)
        date_sprite = pygame.transform.rotate(date_sprite, 270)
        date_pos = (self.rect[2] - 16, 2)
        self.image.blit(date_sprite, date_pos)
        hh_sprite = render_text(hh_str, self.font_time, 42, self.color_time, bold=True)
        sep_sprite = render_text(":", self.font_time, 42, self.color_time)
        mm_sprite = render_text(mm_str, self.font_time, 42, self.color_time, bold=True)
        self.image.blit(hh_sprite, (1, -4))
        self.image.blit(sep_sprite, (44, -8))
        self.image.blit(mm_sprite, (61, -4))
        self.dirty = 1

    def poop(self) -> None:
        logger.info("POOP")
