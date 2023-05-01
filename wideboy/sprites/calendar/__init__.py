import logging
from datetime import datetime, timedelta
from pygame import Clock, Color, Event, Rect, Surface, SRCALPHA

# from wideboy.mqtt.homeassistant import HASS
from wideboy.sprites.image_helpers import render_text
from wideboy.constants import EVENT_EPOCH_SECOND, EVENT_EPOCH_HOUR
from wideboy.sprites.base import BaseSprite
from wideboy.scenes.base import BaseScene


logger = logging.getLogger("sprite.calendar")


class CalendarSprite(BaseSprite):
    rect: Rect
    image: Surface

    def __init__(
        self,
        scene: BaseScene,
        rect: Rect,
        entity_id: str,
        event_count: int = 5,
        max_label_width: int = 64,
        color_fg: Color = Color(255, 255, 255, 255),
        font: str = "fonts/bitstream-vera.ttf",
        font_size: int = 10,
        interval: int = 10,
        days_ahead: int = 60,
    ) -> None:
        super().__init__(scene, rect)
        self.entity_id = entity_id
        self.event_count = event_count
        self.max_label_width = max_label_width
        self.color_fg = color_fg
        self.font = font
        self.font_size = font_size
        self.interval = interval
        self.days_ahead = days_ahead
        self.image = Surface((rect.width, rect.height), SRCALPHA)
        self.calendar_events = []
        self.event_index = 0
        self.update_events()
        self.dirty = 1
        self.render()

    def update(
        self,
        frame: str,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(frame, clock, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_HOUR:
                self.update_events()
            if event.type == EVENT_EPOCH_SECOND and event.unit % self.interval == 0:
                self.dirty = 1
                self.render()
                self.event_index += 1
                if self.event_index > len(self.calendar_events) - 1:
                    self.event_index = 0

    def update_events(self) -> None:
        self.calendar_events = self.get_calendar_events()
        self.event_index = 0

    def render_event_text(self, event: dict) -> Surface:
        start_date = event["start"]["date"]
        ddmm_str = f"{start_date[8:10]}/{start_date[5:7]}"
        label = self.truncate_label(event["summary"])
        return render_text(
            f"{ddmm_str} {label}",
            self.font,
            self.font_size,
            color_bg=Color(0, 0, 0, 0),
            color_fg=self.color_fg,
            color_outline=Color(0, 0, 0, 255),
        )

    def render(self) -> None:
        if not len(self.calendar_events):
            return
        event_surface = self.render_event_text(self.calendar_events[self.event_index])
        self.image.fill(Color(0, 0, 0, 0))
        self.image.blit(
            event_surface,
            (
                (self.rect.width / 2) - (event_surface.get_width() / 2),
                0,
            ),
        )

    def get_calendar_events(self) -> list[dict]:
        now = datetime.now()
        then = now + timedelta(days=self.days_ahead)
        start = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end = then.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        try:
            with self.scene.engine.hass.client as hass:
                events = hass.request(
                    f"calendars/{self.entity_id}?start={start}&end={end}"
                )
            return sorted(events, key=lambda event: event["start"]["date"])
        except:
            logger.error("Failed to get calendar events")
            return []

    def truncate_label(self, label: str) -> str:
        if len(label) <= self.max_label_width:
            return label
        return label[: self.max_label_width - 3] + "..."
