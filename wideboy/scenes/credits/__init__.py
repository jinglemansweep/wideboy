import asyncio
import logging
import pygame

from wideboy.scenes.animation import Act, Animation
from wideboy.sprites.image import ImageSprite
from wideboy.scenes.base import BaseScene
from wideboy.state import DEVICE_ID
from wideboy.utils.pygame import EVENT_EPOCH_MINUTE
from wideboy.config import settings


logger = logging.getLogger(__name__)


class CreditsScene(BaseScene):
    name = "credits"

    def __init__(
        self,
        surface: pygame.surface.Surface,
        bg_color: pygame.color.Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, bg_color)

    def setup(self):
        super().setup()
        # Setup background widget
        self.logo = ImageSprite(
            pygame.Rect(
                self.width - 235,
                4,
                self.width,
                self.height,
            ),
            (self.width, self.height - 8),
            "images/logo.png",
            255,
        )
        self.group.add(self.logo)

    def update(
        self,
        delta: float,
        events: list[pygame.event.Event],
    ) -> None:
        super().update(delta, events)

    # Handle Events

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
