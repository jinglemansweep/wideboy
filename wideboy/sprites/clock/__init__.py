import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.utils.pygame import EVENT_EPOCH_SECOND, EVENT_EPOCH_MINUTE
from wideboy.utils.state import StateStore
from wideboy.sprites import BaseSprite


logger = logging.getLogger("sprites.clock")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']


class ClockSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        font_date: str = "bitstreamverasans",
        font_time: str = "molot",
        color_bg: pygame.color.Color = (0, 0, 0),
        color_fg: pygame.color.Color = (255, 255, 255),
        antialias: bool = True,
        time_fmt: str = "%H:%M",
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        pygame.font.init()
        self.font_date = pygame.font.SysFont(font_date, 20, bold=True)
        self.font_time = pygame.font.SysFont(font_time, 48)
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.antialias = antialias
        self.time_fmt = time_fmt
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
        dow_str = now.strftime("%A")[:3]
        ddmm_str = now.strftime("%d/%m")
        date_str = f"{dow_str} {ddmm_str}"
        time_str = now.strftime(self.time_fmt)
        shadow_depth = 2
        self.image.fill(self.color_bg)
        date_sprite = self.font_date.render(date_str, self.antialias, self.color_fg)
        date_sprite_shadow = self.font_date.render(date_str, self.antialias, (0, 0, 0))
        date_pos = ((self.rect[2] - date_sprite.get_rect()[2]) // 2, 40)
        time_sprite = self.font_time.render(time_str, self.antialias, self.color_fg)
        time_sprite_shadow = self.font_time.render(time_str, self.antialias, (0, 0, 0))
        time_pos = ((self.rect[2] - time_sprite.get_rect()[2]) // 2, -8)
        self.image.blit(
            date_sprite_shadow, (date_pos[0] + shadow_depth, date_pos[1] + shadow_depth)
        )
        self.image.blit(date_sprite, date_pos)
        self.image.blit(
            time_sprite_shadow,
            (time_pos[0] + shadow_depth, time_pos[1] + shadow_depth),
        )
        self.image.blit(time_sprite, time_pos)
        self.dirty = 1

    def poop(self) -> None:
        logger.info("POOP")
