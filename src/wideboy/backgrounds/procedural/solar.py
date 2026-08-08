from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect

_PLANETS = [
    ("Mercury", 0.39, 0.241, 2.0, (170, 170, 170), 0.3),
    ("Venus", 0.72, 0.615, 3.0, (230, 200, 130), 1.7),
    ("Earth", 1.00, 1.000, 3.0, (80, 140, 220), 4.1),
    ("Mars", 1.52, 1.881, 2.5, (210, 100, 60), 2.5),
    ("Jupiter", 5.20, 11.86, 5.5, (210, 170, 120), 5.3),
    ("Saturn", 9.58, 29.46, 5.0, (220, 200, 150), 0.9),
    ("Uranus", 19.2, 84.01, 4.0, (150, 220, 220), 3.7),
    ("Neptune", 30.05, 164.8, 4.0, (80, 120, 200), 2.1),
]

_GLOBAL_TILT = math.radians(14)
_MERCURY_PERIOD = 6.0
_EARTH_OMEGA = 2 * math.pi / (_MERCURY_PERIOD / 0.241)
_N_STARS = 120
_SUN_RADIUS = 4.0
_SUN_GLOW = 16.0
_SUN_CORE = np.array([255, 240, 180], dtype=np.float32)
_SUN_GLOW_C = np.array([255, 160, 40], dtype=np.float32)
_MAX_AU = 30.05
_ORBIT_PTS = 80


class _SolarEffect(Effect):
    name = "solar"
    default_palette = "mono"
    tags = ("nature", "calm", "dark")

    def __init__(self) -> None:
        self._rng = np.random.RandomState(42)
        self._stars_x: np.ndarray | None = None
        self._stars_y: np.ndarray | None = None
        self._stars_phase: np.ndarray | None = None
        self._stars_bright: np.ndarray | None = None
        self._planet_data: list[tuple[float, float, float, float, tuple, float]] | None = None
        self._orbits: list[np.ndarray] | None = None
        self._w = 0
        self._h = 0

    def _init(self, w: int, h: int) -> None:
        self._w, self._h = w, h
        cx, cy = w / 2, h / 2
        max_vy = h / 2 - 4
        d_scale = (w * 0.42) / math.sqrt(_MAX_AU)

        self._planet_data = []
        self._orbits = []
        for _, au, period, size, color_rgb, theta0 in _PLANETS:
            d = d_scale * math.sqrt(au)
            if d > max_vy:
                tilt = min(_GLOBAL_TILT, math.asin(max_vy / d))
            else:
                tilt = _GLOBAL_TILT
            self._planet_data.append((d, tilt, period, size, color_rgb, theta0))
            angles = np.linspace(0, 2 * math.pi, _ORBIT_PTS, endpoint=False)
            ex = cx + d * np.cos(angles)
            ey = cy + d * np.sin(angles) * math.sin(tilt)
            self._orbits.append(np.column_stack([ex, ey]))

        n = _N_STARS
        self._stars_x = self._rng.randint(0, w, n).astype(np.float32)
        self._stars_y = self._rng.randint(0, h, n).astype(np.float32)
        self._stars_phase = self._rng.uniform(0, 2 * math.pi, n).astype(np.float32)
        self._stars_bright = self._rng.uniform(0.3, 1.0, n).astype(np.float32)

    @staticmethod
    def _draw_disc(
        frame: np.ndarray, cx: float, cy: float, r: float, color: np.ndarray, w: int, h: int
    ) -> None:
        r_int = int(r) + 1
        y0 = max(0, int(cy) - r_int)
        y1 = min(h, int(cy) + r_int + 1)
        x0 = max(0, int(cx) - r_int)
        x1 = min(w, int(cx) + r_int + 1)
        if y0 >= y1 or x0 >= x1:
            return
        ys = np.arange(y0, y1, dtype=np.float32)[:, np.newaxis]
        xs = np.arange(x0, x1, dtype=np.float32)
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        mask = dist <= r
        edge = np.clip((r - dist) / 1.5, 0, 1)[..., np.newaxis]
        blended = color * edge + frame[y0:y1, x0:x1] * (1 - edge)
        frame[y0:y1, x0:x1] = np.where(mask[..., np.newaxis], blended, frame[y0:y1, x0:x1])

    @staticmethod
    def _draw_sun(
        frame: np.ndarray,
        cx: float,
        cy: float,
        core_r: float,
        glow_r: float,
        w: int,
        h: int,
    ) -> None:
        gi = int(glow_r) + 1
        y0 = max(0, int(cy) - gi)
        y1 = min(h, int(cy) + gi + 1)
        x0 = max(0, int(cx) - gi)
        x1 = min(w, int(cx) + gi + 1)
        if y0 >= y1 or x0 >= x1:
            return
        ys = np.arange(y0, y1, dtype=np.float32)[:, np.newaxis]
        xs = np.arange(x0, x1, dtype=np.float32)
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        glow = np.exp(-(dist**2) / (2 * (glow_r * 0.4) ** 2))
        intensity = glow[..., np.newaxis]
        frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - intensity) + _SUN_GLOW_C * intensity
        mask = dist <= core_r
        frame[y0:y1, x0:x1] = np.where(mask[..., np.newaxis], _SUN_CORE, frame[y0:y1, x0:x1])

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._stars_x is None or self._w != w or self._h != h:
            self._init(w, h)

        dim = np.array(palette.dim, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)

        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:] = dim

        cx, cy = w / 2, h / 2

        for i in range(_N_STARS):
            sx = int(self._stars_x[i])
            sy = int(self._stars_y[i])
            twinkle = 0.7 + 0.3 * math.sin(t * 2.0 + float(self._stars_phase[i]))
            b = float(self._stars_bright[i]) * twinkle * 0.6
            frame[sy, sx] = np.maximum(frame[sy, sx], dim * (1 - b) + hi * b)

        orbit_color = np.clip(dim * 1.6, 0, 255)
        for pts in self._orbits:
            for i in range(0, len(pts), 5):
                px, py = int(pts[i, 0]), int(pts[i, 1])
                if 0 <= px < w and 0 <= py < h:
                    frame[py, px] = np.maximum(frame[py, px], orbit_color)

        bodies: list[tuple[float, float, float, float, np.ndarray, bool]] = []

        pulse = 0.3 * math.sin(t * 1.5)
        bodies.append((0.0, cx, cy, _SUN_RADIUS + pulse, _SUN_CORE, True))
        _glow_r = _SUN_GLOW + pulse

        for d, tilt, period, size, color_rgb, theta0 in self._planet_data:
            theta = theta0 + _EARTH_OMEGA * t / period
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            px = cx + d * cos_t
            py = cy + d * sin_t * math.sin(tilt)
            depth = sin_t
            size_mult = 1.0 + depth * 0.35
            r = max(1.5, size * size_mult)
            bright = 0.55 + 0.45 * (depth + 1) * 0.5
            body_color = np.array(color_rgb, dtype=np.float32) * bright
            bodies.append((depth, px, py, r, body_color, False))

        bodies.sort(key=lambda b: b[0])

        for depth, px, py, r, color, is_sun in bodies:
            if is_sun:
                self._draw_sun(frame, px, py, r, _glow_r, w, h)
            else:
                self._draw_disc(frame, px, py, r, color, w, h)

        return np.clip(frame, 0, 255).astype(np.uint8)


solar = _SolarEffect()
