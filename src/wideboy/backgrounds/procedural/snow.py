from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _SnowEffect(Effect):
    name = "snow"
    default_palette = "mono"
    tags = ("particle", "calm")

    _N_FLAKES = 200
    _MAX_HEIGHT_RATIO = 0.6
    _SETTLE_AMOUNT = 3.0
    _CYCLE = 30.0
    _MELT_START = 0.7
    _SLIDE_THRESHOLD = 2.5

    def __init__(self) -> None:
        self._rng = np.random.RandomState(42)
        self._hm: np.ndarray | None = None
        self._prev_t = -1.0
        self._w = 0
        self._h = 0
        self._x: np.ndarray | None = None
        self._y: np.ndarray | None = None
        self._vy: np.ndarray | None = None
        self._brightness: np.ndarray | None = None
        self._drift_phase: np.ndarray | None = None
        self._drift_amp: np.ndarray | None = None

    def _init(self, w: int, h: int) -> None:
        n = self._N_FLAKES
        self._hm = np.zeros(w, dtype=np.float32)
        self._x = self._rng.uniform(0, w, n).astype(np.float32)
        self._y = self._rng.uniform(-h * 2, h, n).astype(np.float32)
        self._vy = self._rng.uniform(10, 35, n).astype(np.float32)
        self._brightness = self._rng.uniform(0.4, 1.0, n).astype(np.float32)
        self._drift_phase = self._rng.uniform(0, 2 * np.pi, n).astype(np.float32)
        self._drift_amp = self._rng.uniform(0.3, 2.0, n).astype(np.float32)
        self._w, self._h = w, h

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._hm is None or self._w != w or self._h != h:
            self._init(w, h)

        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        self._prev_t = t

        phase = (t % self._CYCLE) / self._CYCLE
        if phase >= self._MELT_START:
            melt_rate = (phase - self._MELT_START) / (1.0 - self._MELT_START)
            self._hm *= (1.0 - melt_rate * dt * 2.0)

        dim = np.array(palette.dim, dtype=np.uint8)
        hi = np.array(palette.highlight, dtype=np.float32)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim

        self._y += self._vy * dt
        self._x += np.sin(t * 2 + self._drift_phase) * self._drift_amp * dt * 8
        self._x %= w

        ix = np.clip(self._x.astype(np.int32), 0, w - 1)
        iy = self._y.astype(np.int32)
        max_hm = h * self._MAX_HEIGHT_RATIO

        for i in range(self._N_FLAKES):
            xi = ix[i]
            surface_y = h - int(self._hm[xi])
            if self._y[i] >= surface_y:
                if self._hm[xi] < max_hm:
                    self._hm[xi] = min(self._hm[xi] + self._SETTLE_AMOUNT, max_hm)
                    for dx in (-1, 1):
                        nx = xi + dx
                        if 0 <= nx < w and self._hm[nx] < max_hm:
                            self._hm[nx] = min(
                                self._hm[nx] + self._SETTLE_AMOUNT * 0.3,
                                max_hm,
                            )
                self._y[i] = self._rng.uniform(-h * 1.5, -5)
                self._x[i] = self._rng.uniform(0, w)
                ix[i] = int(self._x[i]) % w

        for x in range(1, w - 1):
            h_center = self._hm[x]
            if h_center < self._SLIDE_THRESHOLD:
                continue
            h_left = self._hm[x - 1]
            h_right = self._hm[x + 1]
            diff_left = h_center - h_left
            diff_right = h_center - h_right
            if diff_left > self._SLIDE_THRESHOLD or diff_right > self._SLIDE_THRESHOLD:
                slide_amount = min(h_center * 0.15, 1.5)
                if diff_left > diff_right and h_left < max_hm:
                    self._hm[x] -= slide_amount
                    self._hm[x - 1] = min(self._hm[x - 1] + slide_amount, max_hm)
                elif diff_right > self._SLIDE_THRESHOLD and h_right < max_hm:
                    self._hm[x] -= slide_amount
                    self._hm[x + 1] = min(self._hm[x + 1] + slide_amount, max_hm)

        hm_int = np.clip(self._hm.astype(np.int32), 0, h)
        snow_color = (dim.astype(np.float32) * 0.3 + hi * 0.7).astype(np.uint8)
        for x in range(w):
            sh = hm_int[x]
            if sh > 0:
                frame[h - sh:h, x] = snow_color

        for i in range(self._N_FLAKES):
            yi = iy[i]
            xi = ix[i]
            if 0 <= yi < h:
                b = self._brightness[i]
                color = (dim.astype(np.float32) * (1 - b) + hi * b).astype(np.uint8)
                frame[yi, xi] = color
                glow = (dim.astype(np.float32) * (1 - b * 0.3) + hi * b * 0.3).astype(np.uint8)
                if xi > 0:
                    frame[yi, xi - 1] = glow
                if xi < w - 1:
                    frame[yi, xi + 1] = glow

        return frame


snow = _SnowEffect()
