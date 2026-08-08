from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _RingsEffect(Effect):
    name = "rings"
    default_palette = "sunset"
    tags = ("geometric", "calm")

    _N_RINGS = 6

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        pri = np.array(palette.primary, dtype=np.float32)
        sec = np.array(palette.secondary, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)
        ring_colors = [pri, sec, acc, pri, sec, acc][:self._N_RINGS]

        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = np.array(palette.dim, dtype=np.float32)
        centers = [
            (w // 4, h // 2),
            (w // 2, h // 2),
            (3 * w // 4, h // 2),
            (w // 3, h // 3),
            (2 * w // 3, h // 3),
            (w // 2, 2 * h // 3),
        ][:self._N_RINGS]
        max_radius = h * 1.5
        ring_width = h / 4.0
        ys = np.arange(h, dtype=np.float32)[:, np.newaxis]
        xs = np.arange(w, dtype=np.float32)

        for i, (cx, cy) in enumerate(centers):
            speed = 0.15 + i * 0.05
            phase = (t * speed + i * 1.5) % 5.0
            radius = (phase / 5.0) * max_radius
            if radius < 2:
                continue
            dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
            ring = np.exp(-((dist - radius) ** 2) / (2 * ring_width ** 2))
            fade = max(0, 1.0 - phase / 5.0)
            intensity = (ring * fade)[..., np.newaxis]
            color = ring_colors[i]
            frame = frame * (1 - intensity) + color[np.newaxis, np.newaxis, :] * intensity

        return frame.astype(np.uint8)


rings = _RingsEffect()
