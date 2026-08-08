from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _GradientEffect(Effect):
    name = "gradient"
    default_palette = "ocean"
    tags = ("abstract", "calm")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        colors = palette_array(palette)
        xs = np.arange(w, dtype=np.float32)
        period = w * 2
        offset = (t * 50) % period
        shifted = (xs + offset) % period
        pos = np.where(shifted < w, shifted / w, (period - shifted) / w)
        rgb = sample_palette(colors, pos)
        row = rgb[:, np.newaxis, :]
        broadcast = np.broadcast_to(row, (w, h, 3))
        return broadcast.transpose(1, 0, 2).copy().astype(np.uint8)


gradient_scroll = _GradientEffect()
