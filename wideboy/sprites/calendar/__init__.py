import logging
import pygame
from datetime import datetime
from pygame import SRCALPHA
from wideboy.sprites.image_helpers import render_text
from wideboy.constants import EVENT_EPOCH_SECOND
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.calendar")

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']

import pygame


class CalendarSprite(BaseSprite):
    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.events = []
        self.font = pygame.font.Font(None, 20)
        self.max_width = 200
        self.line_spacing = 25
        self.image = pygame.Surface((self.max_width, self.line_spacing * 5))
        self.rect = self.image.get_rect()

    def add_event(self, event_type, label_text, icon):
        self.events.append({"type": event_type, "label": label_text, "icon": icon})

    def draw_events(self):
        self.image.fill((255, 255, 255))
        y_offset = 0
        for event in self.events[:5]:
            label = event["label"]
            label_width = self.font.size(label)[0]
            if label_width > self.max_width:
                label = (
                    label[
                        : int(self.max_width / self.font.size(label)[0] * len(label))
                        - 3
                    ]
                    + "..."
                )
            label_text = self.font.render(label, True, (0, 0, 0))
            icon = event["icon"]
            icon_rect = icon.get_rect()
            icon_rect.x = 0
            icon_rect.y = y_offset
            self.image.blit(icon, icon_rect)
            label_rect = label_text.get_rect()
            label_rect.x = icon_rect.width + 5
            label_rect.y = y_offset + (self.line_spacing - label_rect.height) / 2
            self.image.blit(label_text, label_rect)
            y_offset += self.line_spacing
