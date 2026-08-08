from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _BubblesEffect(Effect):
    name = "bubbles"
    default_palette = "ocean"
    tags = ("particle", "calm")

    _N_BUBBLES = 12

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        pri = np.array(palette.primary, dtype=np.float32)
        sec = np.array(palette.secondary, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)
        bubble_colors = [pri, sec, acc, pri, sec, acc, pri, sec, acc, pri, sec, acc]

        frame = np.zeros((h, w, 3), dtype=np.float32)
        dim = np.array(palette.dim, dtype=np.float32)
        frame[:, :] = dim
        rng = np.random.RandomState(42)
        n = self._N_BUBBLES
        base_x = rng.randint(10, w - 10, n)
        base_y = rng.uniform(h, h * 2, n)
        speed = rng.uniform(0.5, 1.5, n)
        radius = rng.randint(3, 7, n)
        for i in range(n):
            cy = base_y[i] - t * speed[i] * 20
            cy = cy % (h + radius[i] * 2) - radius[i]
            cx = base_x[i] + np.sin(t * 1.5 + i * 0.7) * 8
            r = radius[i]
            r_int = int(r) + 1
            y0 = max(0, int(cy) - r_int)
            y1 = min(h, int(cy) + r_int + 1)
            x0 = max(0, int(cx) - r_int)
            x1 = min(w, int(cx) + r_int + 1)
            if y0 >= y1 or x0 >= x1:
                continue
            ys = np.arange(y0, y1, dtype=np.float32)[:, np.newaxis]
            xs = np.arange(x0, x1, dtype=np.float32)
            dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
            mask = dist <= r
            edge = np.clip((r - dist) / 2.0, 0, 1)[..., np.newaxis]
            color = bubble_colors[i]
            blended = dim * (1 - edge) + color * edge
            frame[y0:y1, x0:x1] = np.where(mask[..., np.newaxis], blended, frame[y0:y1, x0:x1])
        return frame.astype(np.uint8)


bubbles = _BubblesEffect()
