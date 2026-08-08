from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _TrafficEffect(Effect):
    name = "traffic"
    default_palette = "neon"
    tags = ("linear", "energetic")

    _N_CARS = 10

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        dim = np.array(palette.dim, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        car_palette_colors = [
            np.array(palette.primary, dtype=np.float32),
            np.array(palette.secondary, dtype=np.float32),
            np.array(palette.accent, dtype=np.float32),
        ]

        frame = np.zeros((h, w, 3), dtype=np.float32)

        base_angle = 14
        wobble = math.sin(t * 0.6) * 10
        angle_rad = math.radians(base_angle + wobble)
        tan_a = math.tan(angle_rad)
        road_half_h = 20
        road_color = np.array([50, 50, 50], dtype=np.float32)
        center_y = h // 2

        wobble_amplitude = 5
        wobble_freq = 2.5
        world_speed = 40.0

        xs = np.arange(w, dtype=np.float32)
        wave_offsets = np.sin(xs / w * math.pi * wobble_freq + t * 1.2) * wobble_amplitude

        x_indices = np.arange(w, dtype=np.int32)
        prev_dx = int(-road_half_h * tan_a)
        for dy in range(-road_half_h, road_half_h + 1):
            ys = (center_y + dy + wave_offsets).astype(np.int32)
            dx = int(dy * tan_a)
            for fill_dx in range(min(prev_dx, dx), max(prev_dx, dx) + 1):
                sxs = x_indices - fill_dx
                valid = (ys >= 0) & (ys < h) & (sxs >= 0) & (sxs < w)
                frame[ys[valid], sxs[valid]] = road_color
            prev_dx = dx

        scroll_offset = t * world_speed
        center_ys = (center_y + wave_offsets).astype(np.int32)
        dash_mask = ((x_indices + int(scroll_offset)) % 16) < 8
        valid_center = (center_ys >= 0) & (center_ys < h) & dash_mask
        frame[center_ys[valid_center], x_indices[valid_center]] = hi

        tree_rng = np.random.RandomState(99)
        n_trees = 30
        tree_base_x = tree_rng.uniform(0, w * 2, n_trees)
        tree_side = tree_rng.choice([-1, 1], n_trees)
        tree_dist = tree_rng.uniform(road_half_h + 4, road_half_h + 14, n_trees)
        tree_radius = tree_rng.uniform(3.0, 6.0, n_trees)
        tree_color_variants = [
            np.array([30, 100, 30], dtype=np.float32),
            np.array([20, 80, 20], dtype=np.float32),
            np.array([40, 120, 40], dtype=np.float32),
            np.array([25, 70, 35], dtype=np.float32),
        ]
        tree_color_assign = tree_rng.randint(0, len(tree_color_variants), n_trees)
        tree_trunk_color = np.array([80, 50, 20], dtype=np.float32)

        for ti in range(n_trees):
            tx = (tree_base_x[ti] - t * world_speed) % (w * 2) - w // 2
            itx = int(tx)
            if itx < -8 or itx >= w + 8:
                continue
            mid_x = max(0, min(w - 1, itx))
            local_wave = wave_offsets[mid_x]
            ty = int(center_y + tree_side[ti] * tree_dist[ti] + local_wave)
            r = tree_radius[ti]
            ir = int(r) + 1
            t_color = tree_color_variants[tree_color_assign[ti]]

            y0 = max(0, ty - ir)
            y1 = min(h, ty + ir + 1)
            x0 = max(0, itx - ir)
            x1 = min(w, itx + ir + 1)
            if y0 >= y1 or x0 >= x1:
                continue

            t_ys = np.arange(y0, y1, dtype=np.float32)[:, np.newaxis]
            t_xs = np.arange(x0, x1, dtype=np.float32)
            dist = np.sqrt((t_xs - itx) ** 2 + (t_ys - ty) ** 2)
            mask = dist <= r
            if not np.any(mask):
                continue
            shadow = np.clip((r - dist) / 2.0, 0, 1)
            blended = (
                dim[np.newaxis, np.newaxis, :] * (1 - shadow[..., np.newaxis])
                + t_color * shadow[..., np.newaxis]
            )
            existing = frame[y0:y1, x0:x1]
            frame[y0:y1, x0:x1] = np.where(mask[..., np.newaxis], blended, existing)

            trunk_r = max(1, int(r * 0.25))
            ty0 = max(0, ty - trunk_r)
            ty1 = min(h, ty + trunk_r + 1)
            tx0 = max(0, itx - trunk_r)
            tx1 = min(w, itx + trunk_r + 1)
            if ty0 < ty1 and tx0 < tx1:
                frame[ty0:ty1, tx0:tx1] = tree_trunk_color

        rng = np.random.RandomState(42)
        n_cars = self._N_CARS
        car_w = 14
        car_h = 6
        trail_len = 12
        lanes = rng.randint(0, 2, n_cars)
        base_x = rng.uniform(0, w * 2, n_cars)
        speed = rng.uniform(0.5, 2.0, n_cars)
        color_idx = rng.randint(0, 3, n_cars)

        for i in range(n_cars):
            lane = lanes[i]
            c_color = car_palette_colors[color_idx[i]]
            if lane == 0:
                cx = (base_x[i] - t * world_speed + t * speed[i] * 20) % (w * 2) - w // 2
            else:
                cx = (base_x[i] - t * world_speed - t * speed[i] * 20) % (w * 2) - w // 2

            ix = int(cx)
            mid_x = max(0, min(w - 1, ix + car_w // 2))
            local_offset = wave_offsets[mid_x]
            lane_y_offset = -16 if lane == 0 else 10
            car_y = int(center_y + lane_y_offset + local_offset)

            if car_y < 0 or car_y + car_h > h:
                continue

            for tx in range(trail_len):
                if lane == 0:
                    px = ix - tx - 1
                else:
                    px = ix + car_w + tx
                if 0 <= px < w:
                    trail_offset = wave_offsets[max(0, min(w - 1, px))]
                    trail_y = int(center_y + lane_y_offset + trail_offset)
                    fade = 1.0 - tx / trail_len
                    blended = dim * (1 - fade * 0.7) + c_color * (fade * 0.7)
                    for py in range(trail_y, min(trail_y + car_h, h)):
                        if py >= 0:
                            frame[py, px] = blended

            for dy in range(car_h):
                py = car_y + dy
                if py < 0 or py >= h:
                    continue
                for dx in range(car_w):
                    px = ix + dx
                    if 0 <= px < w:
                        frame[py, px] = c_color

            if lane == 0:
                hx = ix + car_w
                for hy_off in range(min(2, car_h)):
                    hy = car_y + hy_off
                    if 0 <= hx < w and 0 <= hy < h:
                        frame[hy, hx] = hi
                tx_rear = ix - 1
            else:
                hx = ix - 1
                for hy_off in range(min(2, car_h)):
                    hy = car_y + hy_off
                    if 0 <= hx < w and 0 <= hy < h:
                        frame[hy, hx] = hi
                tx_rear = ix + car_w

            for hy_off in range(min(2, car_h)):
                hy = car_y + hy_off
                if 0 <= tx_rear < w and 0 <= hy < h:
                    frame[hy, tx_rear] = c_color * 0.4 + dim * 0.6

        return frame.astype(np.uint8)


traffic = _TrafficEffect()
