from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _MatrixRainEffect(Effect):
    name = "matrix"
    default_palette = "forest"
    tags = ("retro", "dark")

    _N_STREAMS = 100

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.float32)
        pri = np.array(palette.primary, dtype=np.float32)
        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = dim
        rng = np.random.RandomState(42)
        n = self._N_STREAMS
        base_x = rng.randint(0, w, n)
        base_y = rng.randint(-h, 0, n)
        speed = rng.uniform(1.5, 4.0, n)
        length = rng.randint(3, 8, n)
        for i in range(n):
            x = base_x[i] % w
            head_y = int((base_y[i] + t * speed[i] * 20) % (h + length[i]))
            for j in range(length[i]):
                y = head_y - j
                if 0 <= y < h:
                    b = max(0, 1.0 - j / length[i])
                    frame[y, x] = dim * (1 - b) + pri * b
        return frame.astype(np.uint8)


matrix_rain = _MatrixRainEffect()
