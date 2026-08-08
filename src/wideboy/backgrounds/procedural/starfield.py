from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _StarfieldEffect(Effect):
    name = "starfield"
    default_palette = "mono"
    tags = ("particle", "calm", "dark")

    _N_STARS = 80

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.uint8)
        hi = np.array(palette.highlight, dtype=np.uint8)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim
        rng = np.random.RandomState(42)
        n = self._N_STARS
        base_x = rng.randint(0, w, n)
        base_y = rng.randint(0, h, n)
        brightness = rng.uniform(0.3, 1.0, n)
        speed = rng.uniform(0.5, 3.0, n)
        x = (base_x + t * speed * 30) % w
        for i in range(n):
            ix, iy = int(x[i]) % w, base_y[i]
            b = brightness[i]
            mixed = (dim.astype(np.float32) * (1 - b) + hi.astype(np.float32) * b).astype(np.uint8)
            frame[iy, ix] = mixed
        return frame


starfield = _StarfieldEffect()
