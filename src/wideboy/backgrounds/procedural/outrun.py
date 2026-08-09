from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _OutrunEffect(Effect):
    name = "outrun"
    default_palette = "sunset"
    tags = ("game", "retro", "energetic", "nostalgic")

    _HORIZON = 22
    _CAR_W = 80
    _CAR_H = 36
    _SPEED = 60.0
    _OBJECT_SPEED = 7.0
    _N_TREES = 20
    _N_SIGNS = 6

    _CAMERA_C = 28.0
    _STRIPE_DENSITY = 0.2
    _ROAD_HALF_BOTTOM = 420
    _RUMBLE_FRACTION = 0.06
    _CURVE_STRENGTH = 0.36
    _RECYCLE_RANGE = 24.0
    _NEAR_CLIP = 0.4

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._trees: list[dict] = []
        self._signs: list[dict] = []
        self._mountains: list[tuple[int, int, int]] = []
        self._hills: list[tuple[int, int, int]] = []

    def _init_objects(self, w: int, h: int) -> None:
        rng = np.random.RandomState(42)
        self._trees = []
        for i in range(self._N_TREES):
            self._trees.append(
                {
                    "world_z": rng.uniform(0, self._RECYCLE_RANGE),
                    "side": rng.choice([-1, 1]),
                    "lateral": rng.uniform(8, 18),
                    "height": rng.uniform(28, 44),
                    "color_idx": rng.randint(0, 3),
                }
            )
        self._signs = []
        for i in range(self._N_SIGNS):
            self._signs.append(
                {
                    "world_z": rng.uniform(0, self._RECYCLE_RANGE),
                    "side": rng.choice([-1, 1]),
                    "lateral": rng.uniform(6, 12),
                    "height": rng.uniform(22, 32),
                    "width": rng.uniform(16, 26),
                }
            )
        self._mountains = []
        x = 0
        while x < w * 2:
            mw = rng.randint(40, 100)
            mh = rng.randint(8, 18)
            self._mountains.append((x, mw, mh))
            x += mw + rng.randint(10, 40)
        self._hills = []
        x = 0
        while x < w * 2:
            hw = rng.randint(30, 70)
            hh = rng.randint(5, 12)
            self._hills.append((x, hw, hh))
            x += hw + rng.randint(5, 25)

    def _curve_value(self, scroll: float) -> float:
        return (
            math.sin(scroll * 0.0016) * 0.7
            + math.sin(scroll * 0.0041 + 1.3) * 0.3
            + math.sin(scroll * 0.0083 + 2.7) * 0.12
        )

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h:
            self._w, self._h = w, h
            self._init_objects(w, h)

        pri = np.array(palette.primary, dtype=np.float32)
        sec = np.array(palette.secondary, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        dim = np.array(palette.dim, dtype=np.float32)

        frame = np.zeros((h, w, 3), dtype=np.float32)
        horizon = self._HORIZON
        scroll = t * self._SPEED
        obj_scroll = t * self._OBJECT_SPEED

        # Sky gradient
        sky_blend = np.linspace(0, 1, horizon)[:, np.newaxis, np.newaxis]
        sky_colors = dim * (1 - sky_blend) + sec * sky_blend * 0.4
        frame[:horizon, :] = sky_colors

        grass_light = np.array([20, 70, 20], dtype=np.float32)
        grass_dark = np.array([10, 45, 10], dtype=np.float32)
        road_color = np.array([45, 45, 55], dtype=np.float32)
        road_light = np.array([60, 60, 72], dtype=np.float32)
        rumble_light = np.array([220, 50, 50], dtype=np.float32)
        rumble_dark = np.array([220, 220, 220], dtype=np.float32)

        # ---- Road core: hyperbolic perspective + smooth stripe scroll ----
        road_ys = np.arange(horizon + 1, h)
        depth = (road_ys - horizon).astype(np.float32)
        span = float(h - 1 - horizon)
        world_z = self._CAMERA_C / depth
        scale = depth / span
        half_w = (self._ROAD_HALF_BOTTOM * scale).astype(np.int32)
        rumble_w = np.maximum(
            1, (self._ROAD_HALF_BOTTOM * self._RUMBLE_FRACTION * scale + 1).astype(np.int32)
        )
        rumble_half = half_w + rumble_w

        seg = ((world_z + scroll) * self._STRIPE_DENSITY).astype(np.int32) % 2

        curve_val = self._curve_value(scroll) * self._CURVE_STRENGTH
        n_rows = len(road_ys)
        k = np.arange(n_rows, dtype=np.float32)
        curve_offsets = curve_val * k * (k + 1) / 2.0
        curve_offsets = curve_offsets[::-1]
        road_centers = w / 2 + curve_offsets

        xs = np.arange(w)[np.newaxis, :]
        centers_col = road_centers[:, np.newaxis]
        half_col = half_w[:, np.newaxis]
        rumble_half_col = rumble_half[:, np.newaxis]

        dxs = np.abs(xs - centers_col)
        road_mask = dxs < half_col
        rumble_mask = (dxs >= half_col) & (dxs < rumble_half_col)
        grass_mask = ~road_mask & ~rumble_mask

        seg_col = seg[:, np.newaxis, np.newaxis]
        road_px = np.where(seg_col, road_light, road_color)
        grass_px = np.where(seg_col, grass_light, grass_dark)
        rumble_px = np.where(seg_col, rumble_dark, rumble_light)

        road_region = np.zeros((n_rows, w, 3), dtype=np.float32)
        road_region = np.where(road_mask[:, :, np.newaxis], road_px, road_region)
        road_region = np.where(rumble_mask[:, :, np.newaxis], rumble_px, road_region)
        road_region = np.where(grass_mask[:, :, np.newaxis], grass_px, road_region)
        frame[horizon + 1 : h, :] = road_region

        # Center dashes (synced to seg==0)
        dash_active = (seg == 0)[:, np.newaxis]
        dash_w_px = np.maximum(2, (5 * scale + 0.5).astype(np.int32))[:, np.newaxis]
        dash_pixel_mask = dash_active & (dxs < dash_w_px)
        frame[horizon + 1 : h, :] = np.where(
            dash_pixel_mask[:, :, np.newaxis], hi * 0.85, frame[horizon + 1 : h, :]
        )

        car_x = int(w / 2 + self._curve_value(scroll) * 38)

        # Mountains - vectorized
        for mx, mw, mh in self._mountains:
            px = (mx - scroll * 0.1) % (w * 2)
            if px > w + mw:
                px -= w * 2
            if px + mw < 0 or px > w:
                continue
            x0 = max(0, int(px))
            x1 = min(w, int(px + mw))
            if x0 >= x1:
                continue
            peak_x = int(px + mw / 2)
            xs_arr = np.arange(x0, x1)
            ys_arr = np.arange(horizon)
            xs_grid, ys_grid = np.meshgrid(xs_arr, ys_arr)
            dist_g = np.abs(xs_grid - peak_x) / (mw / 2)
            height_profile = (horizon - mh * (1 - dist_g)).astype(int)
            mask = ys_grid >= height_profile
            if not np.any(mask):
                continue
            blend = ((horizon - ys_arr) / horizon)[:, np.newaxis]
            c = dim * 0.3 + pri * 0.3 * (1 - blend)
            ys_m, xs_m = np.where(mask)
            frame[ys_m, xs_m] = frame[ys_m, xs_m] * 0.3 + c[ys_m] * 0.7

        # Hills - vectorized
        for hx, hw, hh in self._hills:
            px = (hx - scroll * 0.25) % (w * 2)
            if px > w + hw:
                px -= w * 2
            if px + hw < 0 or px > w:
                continue
            x0 = max(0, int(px))
            x1 = min(w, int(px + hw))
            if x0 >= x1:
                continue
            peak_x = int(px + hw / 2)
            xs_arr = np.arange(x0, x1)
            ys_arr = np.arange(horizon)
            xs_grid, ys_grid = np.meshgrid(xs_arr, ys_arr)
            dist_g = np.abs(xs_grid - peak_x) / (hw / 2)
            height_profile = (horizon - hh * (1 - dist_g**2)).astype(int)
            mask = ys_grid >= height_profile
            if not np.any(mask):
                continue
            c = grass_dark * 0.8 + dim * 0.2
            ys_m, xs_m = np.where(mask)
            frame[ys_m, xs_m] = frame[ys_m, xs_m] * 0.5 + c * 0.5

        # Trees - depth-based projection toward camera
        tree_colors = [
            np.array([30, 100, 30], dtype=np.float32),
            np.array([20, 80, 20], dtype=np.float32),
            np.array([40, 120, 40], dtype=np.float32),
        ]
        trunk_color = np.array([60, 40, 20], dtype=np.float32)
        for tree in self._trees:
            current_z = (tree["world_z"] - obj_scroll) % self._RECYCLE_RANGE + self._NEAR_CLIP
            depth = self._CAMERA_C / current_z
            if depth < 0.5:
                continue
            t_scale = depth / span
            y_base = int(horizon + depth)
            if y_base < horizon + 1:
                continue

            depth_clamped = min(depth, span)
            dfb = span - depth_clamped
            t_curve = curve_val * dfb * (dfb + 1) / 2.0
            t_center = w / 2 + t_curve
            t_half = self._ROAD_HALF_BOTTOM * t_scale
            t_rumble = t_half + max(1, self._ROAD_HALF_BOTTOM * self._RUMBLE_FRACTION * t_scale)
            tree_x = int(t_center + tree["side"] * (t_rumble + 3 + tree["lateral"] * t_scale))

            th = int(tree["height"] * t_scale)
            if th < 2:
                continue
            tw = int(th * 0.6)
            trunk_h = max(1, int(th * 0.3))
            trunk_w = max(1, int(tw * 0.2))
            trunk_y0 = max(0, y_base - trunk_h)
            trunk_y1 = min(h, y_base)
            trunk_x0 = max(0, tree_x - trunk_w)
            trunk_x1 = min(w, tree_x + trunk_w + 1)
            if trunk_y0 < trunk_y1 and trunk_x0 < trunk_x1:
                frame[trunk_y0:trunk_y1, trunk_x0:trunk_x1] = trunk_color
            foliage_h = th - trunk_h
            if foliage_h > 0:
                fy0 = max(0, y_base - th)
                fy1 = min(h, y_base - trunk_h)
                fx0 = max(0, tree_x - tw)
                fx1 = min(w, tree_x + tw + 1)
                if fy0 < fy1 and fx0 < fx1:
                    frame[fy0:fy1, fx0:fx1] = tree_colors[tree["color_idx"]]

        # Signs - depth-based projection toward camera
        post_color = np.array([100, 100, 100], dtype=np.float32)
        for sign in self._signs:
            current_z = (sign["world_z"] - obj_scroll) % self._RECYCLE_RANGE + self._NEAR_CLIP
            depth = self._CAMERA_C / current_z
            if depth < 0.5:
                continue
            s_scale = depth / span
            y_base = int(horizon + depth)
            if y_base < horizon + 1:
                continue

            depth_clamped = min(depth, span)
            dfb = span - depth_clamped
            s_curve = curve_val * dfb * (dfb + 1) / 2.0
            s_center = w / 2 + s_curve
            s_half = self._ROAD_HALF_BOTTOM * s_scale
            s_rumble = s_half + max(1, self._ROAD_HALF_BOTTOM * self._RUMBLE_FRACTION * s_scale)
            sign_x = int(s_center + sign["side"] * (s_rumble + 2 + sign["lateral"] * s_scale))

            sh = int(sign["height"] * s_scale)
            sw = int(sign["width"] * s_scale)
            if sh < 2 or sw < 2:
                continue
            post_h = int(sh * 1.5)
            post_w = max(1, int(sw * 0.15))
            py0 = max(0, y_base - post_h)
            py1 = min(h, y_base)
            px0 = max(0, sign_x - post_w)
            px1 = min(w, sign_x + post_w + 1)
            if py0 < py1 and px0 < px1:
                frame[py0:py1, px0:px1] = post_color
            by0 = max(0, y_base - post_h - sh)
            by1 = min(h, y_base - post_h)
            bx0 = max(0, sign_x - sw)
            bx1 = min(w, sign_x + sw + 1)
            if by0 < by1 and bx0 < bx1:
                frame[by0 : by0 + 2, bx0:bx1] = hi
                frame[by1 - 2 : by1, bx0:bx1] = hi
                frame[by0:by1, bx0 : bx0 + 2] = hi
                frame[by0:by1, bx1 - 2 : bx1] = hi
                iy0, iy1 = by0 + 2, by1 - 2
                ix0, ix1 = bx0 + 2, bx1 - 2
                if iy0 < iy1 and ix0 < ix1:
                    frame[iy0:iy1, ix0:ix1] = acc

        # Car - large rear-view, only top half (roof + window + shoulders) visible
        # Sprite is 36 rows; positioned so bottom is clipped below the display
        car_y = h - 19
        car_hw = self._CAR_W // 2
        car_left = max(0, car_x - car_hw)
        car_right = min(w, car_x + car_hw + 1)
        car_window = dim * 0.45
        roof_color = sec
        body_color = pri
        tail_color = np.array([255, 60, 50], dtype=np.float32)

        def _car_row(dy: int, x0: int, x1: int, color: np.ndarray) -> None:
            py = car_y + dy
            if 0 <= py < h and x0 < x1:
                frame[py, x0:x1] = color

        # Roof - tapered at top (rows 0-2 narrow, 3-6 full width)
        roof_narrow0 = max(0, car_x - car_hw + 14)
        roof_narrow1 = min(w, car_x + car_hw - 13)
        for dy in range(3):
            _car_row(dy, roof_narrow0, roof_narrow1, roof_color)
        for dy in range(3, 7):
            _car_row(dy, car_left, car_right, roof_color)

        # Rear window - inset dark glass (rows 7-13)
        win0 = max(0, car_x - car_hw + 8)
        win1 = min(w, car_x + car_hw - 7)
        for dy in range(7, 14):
            _car_row(dy, car_left, car_right, body_color)
            _car_row(dy, win0, win1, car_window)

        # Rear body + tail lights (rows 14-18, the visible bottom edge)
        tail_w = 10
        tl0 = max(0, car_x - car_hw + 4)
        tl1 = min(w, tl0 + tail_w)
        tr0 = max(0, car_x + car_hw - tail_w - 3)
        tr1 = min(w, tr0 + tail_w)
        for dy in range(14, 19):
            _car_row(dy, car_left, car_right, body_color)
        for dy in range(15, 19):
            _car_row(dy, tl0, tl1, tail_color)
            _car_row(dy, tr0, tr1, tail_color)

        return np.clip(frame, 0, 255).astype(np.uint8)


outrun = _OutrunEffect()
