from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _WavesEffect(Effect):
    name = "waves"
    default_palette = "forest"
    tags = ("abstract", "calm")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        xs = np.arange(w, dtype=np.float32)
        ys = np.arange(h, dtype=np.float32)
        wave = np.sin(xs[np.newaxis, :] / 20.0 + t + ys[:, np.newaxis] * 0.3)
        v = (wave + 1) / 2
        rgb = sample_palette(colors, v)
        return rgb.astype(np.uint8)


waves = _WavesEffect()
