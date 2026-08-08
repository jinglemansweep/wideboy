from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _AuroraEffect(Effect):
    name = "aurora"
    default_palette = "ocean"
    tags = ("abstract", "calm", "dark")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        xs = np.arange(w, dtype=np.float32)
        ys = np.arange(h, dtype=np.float32)[:, np.newaxis]
        wave1 = np.sin(xs / 80.0 + t * 0.3) * np.sin(ys / 20.0 + t * 0.2)
        wave2 = np.sin(xs / 60.0 + t * 0.5 + 2.0) * np.cos(ys / 15.0 + t * 0.4)
        combined = (wave1 + wave2) / 2.0
        v = (combined + 1.0) / 2.0
        rgb = sample_palette(colors, v)
        return rgb.astype(np.uint8)


aurora = _AuroraEffect()
