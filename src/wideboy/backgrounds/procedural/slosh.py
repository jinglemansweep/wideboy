from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _SloshEffect(Effect):
    name = "slosh"
    default_palette = "ocean"
    tags = ("liquid", "calm")

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.float32)
        pri = np.array(palette.primary, dtype=np.float32)
        sec = np.array(palette.secondary, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)

        fill_level = 0.4
        base_y = h * (1.0 - fill_level)
        crest_amp = h * 0.38
        period = 10.0
        crest_width = w * 0.22

        xs = np.arange(w, dtype=np.float32)

        phase = (t / period) % 1.0
        if phase < 0.5:
            p = phase / 0.5
            eased = 0.5 * (1 - math.cos(math.pi * p))
            crest_x = eased * w
        else:
            p = (phase - 0.5) / 0.5
            eased = 0.5 * (1 - math.cos(math.pi * p))
            crest_x = (1.0 - eased) * w

        dist = np.abs(xs - crest_x)
        crest = crest_amp * np.exp(-(dist**2) / (2 * (crest_width / 2) ** 2))

        trough_dist = np.abs(xs - (w - crest_x))
        trough = crest_amp * 0.3 * np.exp(-(trough_dist**2) / (2 * (crest_width * 0.8 / 2) ** 2))

        ripples = np.sin(xs / 25.0 + t * 3.0) * 1.0 + np.sin(xs / 12.0 - t * 4.5) * 0.6
        surface = base_y - crest + trough + ripples
        surface = np.clip(surface, 1, h - 2)
        surface_int = surface.astype(np.int32)

        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = dim

        ys = np.arange(h, dtype=np.float32)[:, np.newaxis]
        water_depth = h - surface[np.newaxis, :]
        safe_depth = np.maximum(water_depth, 1.0)
        depth_frac = np.maximum(0.0, ys - surface[np.newaxis, :]) / safe_depth

        water_color = (
            sec[np.newaxis, :] * (1 - depth_frac)[..., np.newaxis]
            + pri[np.newaxis, :] * depth_frac[..., np.newaxis]
        )

        caustic = (np.sin(xs[np.newaxis, :] / 18.0 + t * 1.5) + np.sin(ys / 12.0 + t * 1.0)) * 0.07
        water_color = np.clip(water_color + water_color * caustic[..., np.newaxis], 0, 255)

        below = ys >= surface[np.newaxis, :]
        frame = np.where(below[..., np.newaxis], water_color, frame)

        surf_y = surface_int
        xs_valid = np.arange(w, dtype=np.int32)
        valid = (surf_y >= 1) & (surf_y < h - 1)
        vxs = xs_valid[valid]
        vys = surf_y[valid]
        if len(vxs) > 0:
            frame[vys, vxs] = frame[vys, vxs] * 0.3 + hi * 0.7
            below_v = vys + 1
            bmask = below_v < h
            frame[below_v[bmask], vxs[bmask]] = frame[below_v[bmask], vxs[bmask]] * 0.6 + hi * 0.4

        left_wall_h = base_y - surface[0]
        right_wall_h = base_y - surface[-1]
        for wall_x, wall_h in [(0, left_wall_h), (w - 1, right_wall_h)]:
            if wall_h < 4:
                continue
            intensity = min(1.0, wall_h / (h * 0.25))
            rng = np.random.RandomState(int(t * 15) + wall_x * 7)
            n_drops = int(intensity * 15)
            wall_surf = surface_int[wall_x]
            for _ in range(n_drops):
                dx = rng.randint(0, 20)
                px = dx if wall_x == 0 else w - 1 - dx
                py = rng.randint(max(0, wall_surf - int(wall_h * 0.8)), wall_surf)
                if 0 <= py < h and 0 <= px < w:
                    db = intensity * rng.uniform(0.4, 1.0)
                    frame[py, px] = frame[py, px] * (1 - db) + hi * db

        return frame.astype(np.uint8)


slosh = _SloshEffect()
