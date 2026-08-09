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
    _CAR_H = 19
    _CAR_ANGLE_GENTLE = 6.0
    _CAR_ANGLE_HARD = 10.0
    _SPEED = 60.0
    _OBJECT_SPEED = 7.0
    _N_TREES = 20
    _N_SIGNS = 6

    _CAMERA_C = 28.0
    _STRIPE_DENSITY = 0.2
    _ROAD_HALF_BOTTOM = 420
    _RUMBLE_FRACTION = 0.06
    _CURVE_STRENGTH = 0.36
    _CORNER_SLOWDOWN = 0.45
    _RECYCLE_RANGE = 24.0
    _NEAR_CLIP = 0.4

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._last_t: float | None = None
        self._scroll = 0.0
        self._obj_scroll = 0.0
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

    def _car_angle(self, scroll: float) -> float:
        cv = self._curve_value(scroll)
        if cv > 0.6:
            return self._CAR_ANGLE_HARD
        if cv > 0.2:
            return self._CAR_ANGLE_GENTLE
        if cv < -0.6:
            return -self._CAR_ANGLE_HARD
        if cv < -0.2:
            return -self._CAR_ANGLE_GENTLE
        return 0.0

    def _draw_car(
        self,
        frame: np.ndarray,
        w: int,
        h: int,
        car_x: int,
        roof: np.ndarray,
        body: np.ndarray,
        window: np.ndarray,
        tail: np.ndarray,
        angle_deg: float,
    ) -> None:
        cw, ch = self._CAR_W, self._CAR_H
        pivot_x = cw / 2.0
        pivot_y = ch - 1.0

        sprite = np.zeros((ch, cw, 3), dtype=np.float32)
        mask = np.zeros((ch, cw), dtype=bool)

        def span(y0: int, y1: int, x0: int, x1: int, color: np.ndarray) -> None:
            sprite[y0:y1, x0:x1] = color
            mask[y0:y1, x0:x1] = True

        # Roof - tapered at top (rows 0-2 narrow, 3-6 full width)
        span(0, 3, 14, cw - 13, roof)
        span(3, 7, 0, cw, roof)
        # Rear window band (rows 7-13): body fill + inset glass
        span(7, 14, 0, cw, body)
        span(7, 14, 8, cw - 7, window)
        # Rear body (rows 14-18)
        span(14, 19, 0, cw, body)
        # Tail lights (rows 15-18)
        span(15, 19, 4, 14, tail)
        span(15, 19, cw - 13, cw - 3, tail)

        if angle_deg == 0.0:
            x0 = car_x - cw // 2
            y0 = h - ch
            for dy in range(ch):
                py = y0 + dy
                if 0 <= py < h:
                    frame[py, max(0, x0) : min(w, x0 + cw)] = sprite[dy]
            return

        theta = math.radians(angle_deg)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # Corner offsets from pivot -> rotated bounding box
        corners = np.array(
            [
                [0 - pivot_x, 0 - pivot_y],
                [cw - pivot_x, 0 - pivot_y],
                [cw - pivot_x, ch - pivot_y],
                [0 - pivot_x, ch - pivot_y],
            ],
            dtype=np.float32,
        )
        rx_c = corners[:, 0] * cos_t - corners[:, 1] * sin_t
        ry_c = corners[:, 0] * sin_t + corners[:, 1] * cos_t
        min_x, max_x = rx_c.min(), rx_c.max()
        min_y, max_y = ry_c.min(), ry_c.max()
        canvas_w = int(math.ceil(max_x - min_x)) + 1
        canvas_h = int(math.ceil(max_y - min_y)) + 1

        oy_g, ox_g = np.meshgrid(
            np.arange(canvas_h), np.arange(canvas_w), indexing="ij"
        )
        rx = ox_g + min_x
        ry = oy_g + min_y
        dx = rx * cos_t + ry * sin_t
        dy = -rx * sin_t + ry * cos_t
        sx = (pivot_x + dx + 0.5).astype(np.int32)
        sy = (pivot_y + dy + 0.5).astype(np.int32)
        valid = (sx >= 0) & (sx < cw) & (sy >= 0) & (sy < ch)

        # Screen pivot: bottom-center at (car_x, h-1)
        screen_x = (car_x + ox_g + min_x).astype(np.int32)
        screen_y = (h - 1 + oy_g + min_y).astype(np.int32)
        in_frame = (
            valid & (screen_x >= 0) & (screen_x < w) & (screen_y >= 0) & (screen_y < h)
        )
        ix, iy = np.where(in_frame)
        frame[screen_y[ix, iy], screen_x[ix, iy]] = sprite[sy[ix, iy], sx[ix, iy]]

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
        if self._last_t is None:
            self._last_t = t
        dt = max(0.0, t - self._last_t)
        self._last_t = t
        curve_now = self._curve_value(self._scroll)
        factor = 1.0 - self._CORNER_SLOWDOWN * min(1.0, abs(curve_now))
        self._scroll += dt * self._SPEED * factor
        self._obj_scroll += dt * self._OBJECT_SPEED * factor
        scroll = self._scroll
        obj_scroll = self._obj_scroll

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

        car_x = int(w / 2 - self._curve_value(scroll) * 38)

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

        # Car - large rear-view, rotated to steer into curves
        car_window = dim * 0.45
        roof_color = sec
        body_color = pri
        tail_color = np.array([255, 60, 50], dtype=np.float32)
        self._draw_car(
            frame,
            w,
            h,
            car_x,
            roof_color,
            body_color,
            car_window,
            tail_color,
            self._car_angle(scroll),
        )

        return np.clip(frame, 0, 255).astype(np.uint8)


outrun = _OutrunEffect()
