import logging
import pygame
from datetime import datetime, timedelta
from pygame import SRCALPHA
from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.image_helpers import render_text
from wideboy.constants import EVENT_EPOCH_MINUTE
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.calendar")


class CalendarSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.Rect,
        entity_id: str,
        event_count: int = 1,
        max_label_width: int = 64,
        font: str = "fonts/bitstream-vera.ttf",
        font_size: int = 8,
    ) -> None:
        super().__init__(rect)
        self.entity_id = entity_id
        self.event_count = event_count
        self.max_label_width = max_label_width
        self.font = font
        self.font_size = font_size
        self.image = pygame.Surface((rect.width, rect.height), SRCALPHA)
        self.calendar_events = []
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
            if event.type == EVENT_EPOCH_MINUTE:
                self.render()

    def render(self) -> None:
        self.calendar_events = self.get_calendar_events()
        rendered_events = []
        for event in self.calendar_events[: self.event_count]:
            start_date = event["start"]["date"]
            ddmm_str = f"{start_date[8:10]}/{start_date[5:7]}"
            label = self.truncate_label(event["summary"])
            rendered_event = render_text(
                f"{ddmm_str} {label}",
                self.font,
                self.font_size,
                pygame.Color(255, 255, 0),
            )
            rendered_events.append(rendered_event)
        self.image.fill((0, 0, 0, 0))
        for i, rendered_event in enumerate(rendered_events):
            self.image.blit(
                rendered_event,
                (
                    (self.rect.width / 2) - (rendered_event.get_width() / 2),
                    i * rendered_event.get_height(),
                ),
            )

    def get_calendar_events(self) -> list[dict]:
        now = datetime.now()
        next_year = now + timedelta(days=365)
        start = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end = next_year.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        events = HASS.request(f"calendars/{self.entity_id}?start={start}&end={end}")
        logger.debug(f"EVENTS {events}")
        return sorted(events, key=lambda event: event["start"]["date"])

    def truncate_label(self, label: str) -> str:
        if len(label) <= self.max_label_width:
            return label
        return label[: self.max_label_width - 3] + "..."
