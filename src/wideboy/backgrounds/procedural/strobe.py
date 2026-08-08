from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect

_ROWS = [
    (12, 22, 32.0, 0.9),
    (26, 30, -20.0, 1.25),
    (40, 38, 64.0, 0.9),
    (54, 46, -44.0, 1.25),
]

_EDGE = np.array([100, 100, 100], dtype=np.float32)
_CENTER = np.array([255, 70, 20], dtype=np.float32)


class _StrobeEffect(Effect):
    name = "strobe"
    default_palette = "mono"
    tags = ("retro", "geometric", "linear")

    @staticmethod
    def _stamp(
        frame: np.ndarray,
        cx: float,
        cy: float,
        radius: float,
        color: np.ndarray,
        w: int,
        h: int,
    ) -> None:
        r_int = int(radius) + 1
        y0 = max(0, int(cy) - r_int)
        y1 = min(h, int(cy) + r_int + 1)
        x0 = max(0, int(cx) - r_int)
        x1 = min(w, int(cx) + r_int + 1)
        if y0 >= y1 or x0 >= x1:
            return
        ys = np.arange(y0, y1, dtype=np.float32)[:, np.newaxis]
        xs = np.arange(x0, x1, dtype=np.float32)
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        mask = dist <= radius
        edge = np.clip((radius - dist) / 1.5, 0, 1)[..., np.newaxis]
        blended = color * edge + frame[y0:y1, x0:x1] * (1 - edge)
        frame[y0:y1, x0:x1] = np.where(mask[..., np.newaxis], blended, frame[y0:y1, x0:x1])

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.float32)
        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:] = dim

        half_w = w * 0.5
        for y_c, spacing, speed, size_mult in _ROWS:
            offset = speed * t
            n_start = int(np.floor(-offset / spacing)) - 1
            n_end = int(np.ceil((w - offset) / spacing)) + 1
            radius = 4.0 * size_mult
            for n in range(n_start, n_end):
                x = n * spacing + offset
                factor = max(0.0, 1.0 - abs(x - half_w) / half_w)
                factor *= factor
                color = _EDGE * (1 - factor) + _CENTER * factor
                self._stamp(frame, x, y_c, radius, color, w, h)

        return np.clip(frame, 0, 255).astype(np.uint8)


strobe = _StrobeEffect()
