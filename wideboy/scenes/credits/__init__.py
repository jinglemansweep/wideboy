import logging
from pygame import Clock, Color, Event, Rect, Surface, Vector2

from wideboy.constants import AppMetadata, EVENT_EPOCH_SECOND
from wideboy.sprites.image import ImageSprite
from wideboy.sprites.qrcode import QRCodeSprite
from wideboy.sprites.text import TextSprite
from wideboy.scenes.base import BaseScene


logger = logging.getLogger("scenes.scene.credits")


class CreditsScene(BaseScene):
    name = "credits"

    def __init__(
        self,
        surface: Surface,
        bg_color: Color = (0, 0, 0),
    ) -> None:
        super().__init__(surface, bg_color)

    def setup(self):
        super().setup()
        # Setup background widget
        self.logo = ImageSprite(
            Rect(
                self.width - 256,
                4,
                self.width,
                self.height,
            ),
            (250, 58),
            "images/wideboy/logo.png",
            255,
        )
        self.group.add(self.logo)
        self.qr_widget = QRCodeSprite(
            Rect(2, 2, 64 - 2, 64 - 2),
            AppMetadata.REPO_URL,
            Vector2(60, 60),
        )
        self.group.add(self.qr_widget)
        self.text_version = TextSprite(
            Rect(self.width - 20, self.height - 11, 32, 12),
            AppMetadata.VERSION,
            font_size=7,
            color_fg=Color(128, 128, 128),
        )
        self.group.add(self.text_version)
        self.text_repo_url = TextSprite(
            Rect(66, self.height - 20, 400, 36),
            AppMetadata.REPO_URL,
            font_size=14,
            color_fg=Color(255, 255, 0),
        )
        self.group.add(self.text_repo_url)
        self.text_frame = TextSprite(
            Rect(66, 2, 400, 14),
            "FRAME: 00000000",
            font_size=10,
            color_fg=Color(255, 0, 255),
        )
        self.group.add(self.text_frame)
        self.text_fps = TextSprite(
            Rect(66, 14, 400, 14),
            "FPS: 00.0",
            font_size=10,
            color_fg=Color(255, 0, 255),
        )
        self.group.add(self.text_fps)

    def update(
        self,
        clock: Clock,
        delta: float,
        events: list[Event],
    ) -> None:
        super().update(clock, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND:
                self.text_frame.set_text(f"FRAME: {self.frame}")
                self.text_fps.set_text(f"FPS: {int(clock.get_fps())}")

    # Handle Events

    def handle_events(self, events: list[Event]) -> None:
        super().handle_events(events)
