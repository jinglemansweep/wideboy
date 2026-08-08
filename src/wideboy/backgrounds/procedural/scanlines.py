from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _ScanlinesEffect(Effect):
    name = "scanlines"
    default_palette = "neon"
    tags = ("retro", "dark")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        xs = np.arange(w, dtype=np.float32)
        ys = np.arange(h, dtype=np.float32)[:, np.newaxis]
        base = np.sin(xs / 50.0 + t * 0.8) * 0.3 + 0.5
        scan = np.sin(ys * np.pi + t * 3) * 0.15 + 0.75
        v = np.clip(base * scan, 0.0, 1.0)
        rgb = sample_palette(colors, v)
        return rgb.astype(np.uint8)


scanlines = _ScanlinesEffect()
