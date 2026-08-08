from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _PlasmaEffect(Effect):
    name = "plasma"
    default_palette = "neon"
    tags = ("abstract", "calm")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        xs = np.arange(w, dtype=np.float32)
        ys = np.arange(h, dtype=np.float32)[:, np.newaxis]
        v = (
            np.sin(xs / 32.0 + t)
            + np.sin(ys / 24.0 + t * 0.7)
            + np.sin((xs + ys) / 40.0 + t * 0.5)
            + np.sin(np.sqrt(xs**2 + ys**2) / 30.0 + t * 1.3)
        )
        v = (v + 4) / 8.0
        rgb = sample_palette(colors, v)
        return rgb.astype(np.uint8)


plasma = _PlasmaEffect()
