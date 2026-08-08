from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _LightningEffect(Effect):
    name = "lightning"
    default_palette = "neon"
    tags = ("energetic", "dark")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        hi = np.array(palette.highlight, dtype=np.float32)
        dim = np.array(palette.dim, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)

        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = dim
        flash_interval = 2.5
        flash_duration = 0.15
        phase = t % flash_interval
        if phase > flash_duration:
            return frame.astype(np.uint8)
        flash_intensity = 1.0 - phase / flash_duration
        rng = np.random.RandomState(int(t / flash_interval))
        x = rng.randint(50, w - 50)
        bolt = np.zeros((h, w), dtype=np.float32)
        cx = float(x)
        for y in range(h):
            bolt[y, int(cx) % w] = flash_intensity
            if int(cx) > 0:
                bolt[y, int(cx) - 1] = flash_intensity * 0.5
            if int(cx) < w - 1:
                bolt[y, int(cx) + 1] = flash_intensity * 0.5
            cx += rng.uniform(-3, 3)
            if rng.random() < 0.1:
                branch_x = int(cx) % w
                for dy in range(min(8, h - y)):
                    if 0 <= branch_x < w:
                        bolt[y + dy, branch_x] = flash_intensity * 0.3
                    branch_x += rng.choice([-1, 0, 1])
        bolt = np.clip(bolt, 0, 1)
        bolt_color = bolt[..., np.newaxis] * hi
        ambient = np.ones((h, w, 1)) * (flash_intensity * 0.1) * acc
        frame = frame + bolt_color + ambient
        return np.clip(frame, 0, 255).astype(np.uint8)


lightning = _LightningEffect()
