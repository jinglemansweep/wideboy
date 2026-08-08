from __future__ import annotations

import math
from typing import Any

import numpy as np

from ...render.palette import Palette
from ._base import Effect


def _generate_cave(
    rng: np.random.RandomState, cave_len: int, h: int,
) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int, int, int]], list[int]]:
    levels = 5
    n_pts = (1 << levels) + 1
    step = cave_len / (n_pts - 1)
    center = np.zeros(n_pts, dtype=np.float32)
    center[:] = h / 2.0
    for i in range(n_pts):
        center[i] += math.sin(i * step / 120.0) * 8
        center[i] += rng.uniform(-3, 3)

    for lv in range(levels):
        stride = 1 << (levels - lv)
        offset = rng.uniform(-2.5, 2.5, n_pts)
        for i in range(0, n_pts, stride):
            center[i] += offset[i]
            center[i] = max(12, min(h - 12, center[i]))
        half = stride // 2
        for i in range(half, n_pts - 1, stride):
            center[i] = (center[i - half] + center[i + half]) / 2.0 + offset[i] * 0.5
            center[i] = max(12, min(h - 12, center[i]))

    gap = np.full(n_pts, 52.0, dtype=np.float32)
    for i in range(n_pts):
        gap[i] += math.sin(i * step / 80.0 + 2.0) * 6
        gap[i] = max(44, min(58, gap[i]))

    ceiling = np.zeros(cave_len, dtype=np.float32)
    floor = np.zeros(cave_len, dtype=np.float32)
    for i in range(n_pts - 1):
        x0 = int(i * step)
        x1 = int((i + 1) * step)
        if x1 > cave_len:
            x1 = cave_len
        if x1 > x0 + 1:
            frac = np.arange(x1 - x0, dtype=np.float32) / max(1, x1 - x0 - 1)
        else:
            frac = np.zeros(1, dtype=np.float32)
        c0, c1 = center[i], center[i + 1]
        g0, g1 = gap[i], gap[i + 1]
        for j in range(x1 - x0):
            cx = x0 + j
            if cx < cave_len:
                c = c0 * (1 - frac[min(j, len(frac) - 1)]) + c1 * frac[min(j, len(frac) - 1)]
                g = g0 * (1 - frac[min(j, len(frac) - 1)]) + g1 * frac[min(j, len(frac) - 1)]
                ceiling[cx] = c - g / 2
                floor[cx] = c + g / 2

    n_spikes = rng.randint(8, 13)
    spikes = []
    for _ in range(n_spikes):
        sx = rng.randint(40, cave_len - 40)
        from_ceiling = rng.random() < 0.5
        spike_h = rng.uniform(10, 22)
        spike_w = rng.uniform(6, 14)
        spikes.append((sx, spike_h, spike_w, 1 if from_ceiling else 0))

    n_stops = rng.randint(1, 3)
    stops = sorted(rng.randint(200, cave_len - 200, n_stops).tolist())
    for i in range(1, len(stops)):
        if stops[i] - stops[i - 1] < 200:
            stops[i] = stops[i - 1] + 200

    return ceiling, floor, spikes, stops


class _AirwolfEffect(Effect):
    name = "airwolf"
    default_palette = "mono"
    tags = ("nostalgic", "energetic")

    _CAVE_LEN = 2048
    _WORLD_SPEED = 40.0
    _HELI_SCREEN_X = 120
    _THRUST_UP = 8.0
    _THRUST_PERIOD = 0.6
    _STOP_DURATION = 2.5

    def __init__(self) -> None:
        self._cache: dict[int | str, Any] = {}

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.float32)
        pri = np.array(palette.primary, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)

        cave_len = self._CAVE_LEN
        world_speed = self._WORLD_SPEED
        heli_screen_x = self._HELI_SCREEN_X
        thrust_up = self._THRUST_UP
        thrust_period = self._THRUST_PERIOD
        stop_duration = self._STOP_DURATION

        world_x = t * world_speed
        cave_idx = int(world_x // (cave_len - w)) if cave_len > w else 0
        local_x = world_x % (cave_len - w) if cave_len > w else 0

        if cave_idx not in self._cache or self._cache.get("_idx") != cave_idx:
            rng = np.random.RandomState(cave_idx * 7 + 13)
            ceiling, floor, spikes, stops = _generate_cave(rng, cave_len, h)
            self._cache.clear()
            self._cache["_idx"] = cave_idx
            self._cache["ceiling"] = ceiling
            self._cache["floor"] = floor
            self._cache["spikes"] = spikes
            self._cache["stops"] = stops
            self._cache["stop_entered"] = [False] * len(stops)

        ceiling = self._cache["ceiling"]
        floor = self._cache["floor"]
        spikes = self._cache["spikes"]
        stops = self._cache["stops"]
        stop_entered = self._cache["stop_entered"]

        heli_world_x = int(local_x) + heli_screen_x
        for i, sx in enumerate(stops):
            if not stop_entered[i] and heli_world_x >= sx:
                stop_entered[i] = True
                self._cache["_stop_time"] = t
                self._cache["_stop_x"] = int(local_x)
            if stop_entered[i] and "_stop_time" in self._cache:
                elapsed = t - self._cache["_stop_time"]
                if elapsed < stop_duration:
                    local_x = float(self._cache["_stop_x"])

        heli_world_x = int(local_x) + heli_screen_x

        ceil_at_heli = ceiling[heli_world_x] if heli_world_x < cave_len else h // 4
        floor_at_heli = floor[heli_world_x] if heli_world_x < cave_len else 3 * h // 4

        thrust_phase = (t / thrust_period) % 1.0
        thrust = -thrust_up if thrust_phase < 0.3 else 0.0
        heli_mid = (ceil_at_heli + floor_at_heli) / 2.0
        gap_size = floor_at_heli - ceil_at_heli
        drift_amp = gap_size * 0.3
        drift = math.sin(t * 1.2) * drift_amp + math.sin(t * 2.7) * drift_amp * 0.3
        heli_y = heli_mid + drift + thrust * 0.3
        heli_y = max(ceil_at_heli + 2, min(floor_at_heli - 6, heli_y))
        heli_cy = int(heli_y)
        heli_x_drift = math.sin(t * 0.9) * 60 + math.sin(t * 0.4) * 30
        heli_cx = heli_screen_x + int(heli_x_drift)

        frame = np.zeros((h, w, 3), dtype=np.float32)

        x_start = int(local_x)
        x_end = min(x_start + w, cave_len)
        vis_w = x_end - x_start
        if vis_w > 0:
            ceil_slice = ceiling[x_start:x_end].astype(np.int32)
            floor_slice = floor[x_start:x_end].astype(np.int32)
            ys = np.arange(h, dtype=np.int32)[:, np.newaxis]
            ceil_mask = ys <= ceil_slice[np.newaxis, :]
            floor_mask = ys >= floor_slice[np.newaxis, :]
            wall_mask = ceil_mask | floor_mask
            frame[:, :vis_w] = np.where(wall_mask[..., np.newaxis], dim, frame[:, :vis_w])
            valid_ceil = (ceil_slice >= 0) & (ceil_slice < h)
            frame[ceil_slice[valid_ceil], np.arange(vis_w)[valid_ceil]] = pri * 0.6 + dim * 0.4
            valid_floor = (floor_slice >= 0) & (floor_slice < h)
            frame[floor_slice[valid_floor], np.arange(vis_w)[valid_floor]] = pri * 0.6 + dim * 0.4

        for sx, spike_h, spike_w, from_ceiling in spikes:
            screen_sx = sx - int(local_x)
            if screen_sx + int(spike_w) < 0 or screen_sx >= w:
                continue
            half_w = spike_w / 2.0
            for dx in range(int(spike_w) + 1):
                px = screen_sx + dx
                if px < 0 or px >= w:
                    continue
                frac = 1.0 - abs(dx - half_w) / half_w if half_w > 0 else 0
                sh = spike_h * frac
                if sh < 1:
                    continue
                wx = int(local_x) + px
                if wx < 0 or wx >= cave_len:
                    continue
                if from_ceiling:
                    base = int(ceiling[wx])
                    y0 = base
                    y1 = min(h, base + int(sh))
                else:
                    base = int(floor[wx])
                    y0 = max(0, base - int(sh))
                    y1 = base
                y0 = max(0, y0)
                y1 = min(h, y1)
                if y0 < y1:
                    frame[y0:y1, px] = dim * 0.7 + pri * 0.3
                    if y0 < y1:
                        edge_y = y1 - 1 if from_ceiling else y0
                        if 0 <= edge_y < h:
                            frame[edge_y, px] = pri

        rotor_phase = math.sin(t * 40)
        body_color = hi
        rotor_color = acc
        tail_color = pri * 0.7 + dim * 0.3
        body_pts = [
            (6, 0), (9, 0), (12, 0), (15, 0), (18, 0), (21, 0),
            (24, 0), (27, 0), (30, 0), (33, 0), (36, 0),
            (12, -3), (15, -3), (18, -3), (21, -3), (24, -3), (27, -3),
            (12, 3), (15, 3), (18, 3), (21, 3), (24, 3), (27, 3),
            (6, -3), (9, -3),
            (33, -1), (33, 1), (36, -1), (36, 1),
        ]
        tail_pts = [
            (3, -3), (0, -3), (-3, -3), (-3, -6),
            (-3, -9), (0, -6), (-6, -9),
        ]
        rotor_pts_top = [
            (-6, -9), (-3, -9), (0, -9), (3, -9), (6, -9), (9, -9),
            (12, -9), (15, -9), (18, -9), (21, -9), (24, -9), (27, -9),
            (30, -9), (33, -9), (36, -9), (39, -9), (42, -9),
        ]
        for dx, dy in body_pts:
            px, py = heli_cx + dx, heli_cy + dy
            if 0 <= px < w and 0 <= py < h:
                frame[py, px] = body_color
        for dx, dy in tail_pts:
            px, py = heli_cx + dx, heli_cy + dy
            if 0 <= px < w and 0 <= py < h:
                frame[py, px] = tail_color
        rotor_offset = int(rotor_phase * 12)
        for dx, dy in rotor_pts_top:
            px, py = heli_cx + dx + rotor_offset, heli_cy + dy
            if 0 <= px < w and 0 <= py < h:
                frame[py, px] = frame[py, px] * 0.5 + rotor_color * 0.5
        canopy_pts = [(33, 0), (36, 0), (33, -1), (36, -1)]
        for dx, dy in canopy_pts:
            px, py = heli_cx + dx, heli_cy + dy
            if 0 <= px < w and 0 <= py < h:
                frame[py, px] = acc * 0.6 + hi * 0.4

        near_ceil = False
        near_floor = False
        for check_dx in range(-3, 39, 3):
            wx = int(local_x) + heli_cx + check_dx
            if 0 <= wx < cave_len:
                c = ceiling[wx]
                f = floor[wx]
                if (heli_cy - 9) - c < 8:
                    near_ceil = True
                if f - (heli_cy + 4) < 8:
                    near_floor = True
        if near_ceil or near_floor:
            spark_rng = np.random.RandomState(int(t * 60))
            n_sparks = spark_rng.randint(3, 7)
            for _ in range(n_sparks):
                sx = heli_cx + spark_rng.randint(0, 36)
                if near_ceil:
                    sy = int(ceil_at_heli) + spark_rng.randint(0, 3)
                else:
                    sy = int(floor_at_heli) - spark_rng.randint(1, 4)
                vx = spark_rng.uniform(-8, 8)
                vy = spark_rng.uniform(-6, 6)
                life = spark_rng.uniform(0.05, 0.25)
                for step in range(int(life * 60)):
                    px = int(sx + vx * step / 60)
                    py = int(sy + vy * step / 60)
                    if 0 <= px < w and 0 <= py < h:
                        fade = 1.0 - step / (life * 60)
                        spark_c = hi * fade + dim * (1 - fade)
                        frame[py, px] = np.maximum(frame[py, px], spark_c)

        return frame.astype(np.uint8)


airwolf = _AirwolfEffect()
