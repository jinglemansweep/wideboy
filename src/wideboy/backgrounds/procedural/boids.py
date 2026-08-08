from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _BoidsEffect(Effect):
    name = "boids"
    default_palette = "neon"
    tags = ("nature", "calm", "particle")

    _N_BOIDS = 80
    _MAX_SPEED = 60.0
    _MIN_SPEED = 20.0
    _PERCEPTION = 40.0
    _SEP_WEIGHT = 1.8
    _ALI_WEIGHT = 1.0
    _COH_WEIGHT = 0.5
    _SEP_DIST = 12.0
    _EDGE_MARGIN = 16.0
    _EDGE_WEIGHT = 80.0

    def __init__(self) -> None:
        self._rng = np.random.RandomState(7)
        self._px: np.ndarray | None = None
        self._py: np.ndarray | None = None
        self._vx: np.ndarray | None = None
        self._vy: np.ndarray | None = None
        self._prev_t = -1.0
        self._w = 0
        self._h = 0

    def _init(self, w: int, h: int) -> None:
        n = self._N_BOIDS
        self._px = self._rng.uniform(w * 0.2, w * 0.8, n).astype(np.float32)
        self._py = self._rng.uniform(h * 0.2, h * 0.8, n).astype(np.float32)
        angles = self._rng.uniform(0, 2 * np.pi, n).astype(np.float32)
        speeds = self._rng.uniform(self._MIN_SPEED, self._MAX_SPEED, n).astype(np.float32)
        self._vx = np.cos(angles) * speeds
        self._vy = np.sin(angles) * speeds
        self._w, self._h = w, h

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._px is None or self._w != w or self._h != h:
            self._init(w, h)

        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        self._prev_t = t

        n = self._N_BOIDS
        px, py = self._px, self._py
        vx, vy = self._vx, self._vy

        sep_x = np.zeros(n, dtype=np.float32)
        sep_y = np.zeros(n, dtype=np.float32)
        ali_x = np.zeros(n, dtype=np.float32)
        ali_y = np.zeros(n, dtype=np.float32)
        coh_x = np.zeros(n, dtype=np.float32)
        coh_y = np.zeros(n, dtype=np.float32)

        for i in range(n):
            dx = px - px[i]
            dy = py - py[i]
            dx = np.where(dx > w / 2, dx - w, np.where(dx < -w / 2, dx + w, dx))
            dist = np.sqrt(dx * dx + dy * dy)
            mask = (dist < self._PERCEPTION) & (dist > 0.001)

            if np.any(mask):
                close = dist < self._SEP_DIST
                if np.any(close):
                    sep_x[i] = -np.sum(dx[close] / (dist[close] + 0.01))
                    sep_y[i] = -np.sum(dy[close] / (dist[close] + 0.01))
                ali_x[i] = np.mean(vx[mask]) - vx[i]
                ali_y[i] = np.mean(vy[mask]) - vy[i]
                coh_x[i] = np.mean(dx[mask])
                coh_y[i] = np.mean(dy[mask])

        margin = self._EDGE_MARGIN
        edge_x = np.zeros(n, dtype=np.float32)
        edge_y = np.zeros(n, dtype=np.float32)
        near_left = px < margin
        near_right = px > w - margin
        near_top = py < margin
        near_bottom = py > h - margin
        edge_x = np.where(near_left, (margin - px) / margin, edge_x)
        edge_x = np.where(near_right, -(margin - (w - px)) / margin, edge_x)
        edge_y = np.where(near_top, (margin - py) / margin, edge_y)
        edge_y = np.where(near_bottom, -(margin - (h - py)) / margin, edge_y)

        vx += (
            sep_x * self._SEP_WEIGHT
            + ali_x * self._ALI_WEIGHT
            + coh_x * self._COH_WEIGHT
            + edge_x * self._EDGE_WEIGHT
        ) * dt
        vy += (
            sep_y * self._SEP_WEIGHT
            + ali_y * self._ALI_WEIGHT
            + coh_y * self._COH_WEIGHT
            + edge_y * self._EDGE_WEIGHT
        ) * dt

        speed = np.sqrt(vx * vx + vy * vy)
        too_fast = speed > self._MAX_SPEED
        too_slow = speed < self._MIN_SPEED
        safe_speed = speed + 0.001
        vx = np.where(
            too_fast,
            vx / speed * self._MAX_SPEED,
            np.where(too_slow, vx / safe_speed * self._MIN_SPEED, vx),
        )
        vy = np.where(
            too_fast,
            vy / speed * self._MAX_SPEED,
            np.where(too_slow, vy / safe_speed * self._MIN_SPEED, vy),
        )

        self._px = (px + vx * dt) % w
        self._py = np.clip(py + vy * dt, 0, h - 1)
        self._vx, self._vy = vx, vy

        dim = np.array(palette.dim, dtype=np.float32)
        colors = [
            np.array(palette.primary, dtype=np.float32),
            np.array(palette.secondary, dtype=np.float32),
            np.array(palette.accent, dtype=np.float32),
            np.array(palette.highlight, dtype=np.float32),
        ]

        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = dim

        for i in range(n):
            bx = int(self._px[i])
            by = int(self._py[i])
            if not (0 <= bx < w and 0 <= by < h):
                continue

            angle = math.atan2(self._vy[i], self._vx[i])
            c, s = math.cos(angle), math.sin(angle)
            color = colors[i % len(colors)]

            tip_x = bx + int(c * 8)
            tip_y = by + int(s * 8)
            mid_x = bx + int(c * 4)
            mid_y = by + int(s * 4)
            l_x = bx + int(-c * 3 - s * 4)
            l_y = by + int(-s * 3 + c * 4)
            r_x = bx + int(-c * 3 + s * 4)
            r_y = by + int(-s * 3 - c * 4)
            tail_x = bx + int(-c * 5)
            tail_y = by + int(-s * 5)

            body = [
                (tip_x, tip_y),
                (mid_x, mid_y),
                (mid_x + int(-s), mid_y + int(c)),
                (mid_x + int(s), mid_y - int(c)),
                (bx, by),
                (l_x, l_y),
                (r_x, r_y),
                (tail_x, tail_y),
            ]
            for px_t, py_t in body:
                if 0 <= px_t < w and 0 <= py_t < h:
                    frame[py_t, px_t] = color

            glow = color * 0.35 + dim * 0.65
            for dpx in (-1, 0, 1):
                for dpy in (-1, 0, 1):
                    if dpx == 0 and dpy == 0:
                        continue
                    gx, gy = bx + dpx, by + dpy
                    if 0 <= gx < w and 0 <= gy < h:
                        frame[gy, gx] = np.maximum(frame[gy, gx], glow)

        return np.clip(frame, 0, 255).astype(np.uint8)


boids = _BoidsEffect()
