from __future__ import annotations

from typing import Any

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette


class _MandelbrotEffect(Effect):
    name = "mandelbrot"
    default_palette = "sunset"
    tags = ("abstract", "geometric")

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        cx, cy = -0.745, 0.186
        cycle = 30.0
        max_zoom_exp = 4.0
        t_mod = t % cycle
        phase = t_mod / cycle
        zoom_exp = max_zoom_exp * (1.0 - abs(2.0 * phase - 1.0))
        zoom = 2.0 ** zoom_exp
        max_iter = min(20 + int(5 * zoom_exp), 35)

        cache = self._cache
        cached_t = cache.get("t", -999.0)
        dt = abs(t - cached_t)

        if (
            cache.get("frame") is not None
            and cache.get("shape") == (h, w)
            and cache.get("palette_id") == id(palette)
            and dt < (0.3 if zoom > 16 else 0.05)
        ):
            return cache["frame"]

        aspect = w / h
        half_h = 1.5 / zoom
        half_w = half_h * aspect
        x = np.linspace(cx - half_w, cx + half_w, w, dtype=np.float32)
        y = np.linspace(cy - half_h, cy + half_h, h, dtype=np.float32)
        X, Y = np.meshgrid(x, y)

        C = (X + 1j * Y).astype(np.complex64)

        Z = np.zeros_like(C)
        M = np.full(C.shape, max_iter, dtype=np.float32)
        active = np.ones(C.shape, dtype=bool)

        for i in range(max_iter):
            if not active.any():
                break
            Z[active] = Z[active] ** 2 + C[active]
            escaped = active & (np.abs(Z) > 2.0)
            M[escaped] = i + 1.0 - np.log2(np.log2(np.abs(Z[escaped]) + 1e-10))
            active &= ~escaped

        colors = palette_array(palette)
        interior = M >= max_iter
        norm = M / max_iter
        rgb = sample_palette(colors, norm)
        rgb[interior] = colors[4]
        frame = np.clip(rgb, 0, 255).astype(np.uint8)

        cache["frame"] = frame
        cache["shape"] = (h, w)
        cache["palette_id"] = id(palette)
        cache["t"] = t
        return frame


mandelbrot = _MandelbrotEffect()
