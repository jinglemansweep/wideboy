from __future__ import annotations

import pygame
from PIL import Image


def load_image(path: str) -> pygame.Surface:
    img = Image.open(path).convert("RGBA")
    surf = pygame.image.fromstring(img.tobytes(), img.size, "RGBA")
    return surf.convert_alpha()
