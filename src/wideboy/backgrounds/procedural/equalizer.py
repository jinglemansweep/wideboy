from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _EqualizerEffect(Effect):
    name = "equalizer"
    default_palette = "neon"
    tags = ("retro", "energetic")

    _N_BARS = 32

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = np.array(palette.dim, dtype=np.uint8)
        bar_width = w // self._N_BARS
        rng = np.random.RandomState(42)
        base_heights = rng.random(self._N_BARS)
        speeds = rng.uniform(0.5, 2.0, self._N_BARS)
        for i in range(self._N_BARS):
            height_factor = (np.sin(t * speeds[i] + base_heights[i] * 10) + 1) / 2
            bar_h = int(height_factor * h * 0.9)
            x_start = i * bar_width
            x_end = x_start + bar_width - 1
            if bar_h <= 0:
                continue
            ys = np.arange(h - bar_h, h, dtype=np.float32)
            pos = (h - ys) / max(1, bar_h)
            rgb = sample_palette(colors, pos)
            for yi, y in enumerate(range(h - bar_h, h)):
                frame[y, x_start:x_end] = rgb[yi].astype(np.uint8)
        return frame


equalizer = _EqualizerEffect()
