import logging
import pygame
import qrcode
from pygame import Color, Rect, Surface, Vector2, SRCALPHA
from wideboy.sprites.base import BaseSprite


logger = logging.getLogger("sprite.qrcode")


class QRCodeSprite(BaseSprite):
    def __init__(
        self,
        rect: Rect,
        data: str,
        size: Vector2 = (64, 64),
        color_bg: Color = (255, 255, 255),
        color_fg: Color = (0, 0, 0),
        border: int = 2,
    ) -> None:
        super().__init__(rect)
        self.image = Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.data = data
        self.size = size
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.border = border
        self.render()

    def render(self) -> None:
        qr = qrcode.QRCode(border=self.border)
        qr.add_data(self.data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=self.color_fg, back_color=self.color_bg)
        qr_surface = pygame.image.fromstring(
            qr_img.tobytes(), qr_img.size, qr_img.mode
        ).convert()
        qr_surface_scaled = pygame.transform.scale(qr_surface, self.size)
        self.image.blit(qr_surface_scaled, (0, 0))
        self.dirty = 1
