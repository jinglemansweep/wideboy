from __future__ import annotations

import math

import numpy as np
import pygame

from ...render.palette import Palette
from ._base import Effect


def _to_rgb(c: np.ndarray) -> tuple[int, int, int]:
    return (
        int(max(0.0, min(255.0, c[0]))),
        int(max(0.0, min(255.0, c[1]))),
        int(max(0.0, min(255.0, c[2]))),
    )


class _OutrunEffect(Effect):
    name = "outrun"
    default_palette = "sunset"
    tags = ("game", "retro", "energetic", "nostalgic")

    _HORIZON = 22
    _CAR_YAW_GENTLE = 22.0
    _CAR_YAW_HARD = 40.0
    _CAR_TILT_GENTLE = 2.0
    _CAR_TILT_HARD = 4.0
    _CAR_CANVAS_W = 180
    _CAR_CANVAS_H = 96
    _CAR_CAM_Y = 16.0
    _CAR_CAM_D = 58.0
    _CAR_FOCAL = 70.0
    _CAR_SCY = 50.0
    _CAR_WHEEL_R_MAX = 7
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
    _CURVE_F1 = 0.012
    _CURVE_F2 = 0.028
    _CURVE_F3 = 0.0504
    _CURVE_POW = 2.2
    _RECYCLE_RANGE = 24.0
    _NEAR_CLIP = 0.4

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._last_t: float | None = None
        self._scroll = 0.0
        self._obj_scroll = 0.0
        self._curve_scale = self._compute_curve_scale()
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

    def _curve_raw(self, scroll: float) -> float:
        return (
            math.sin(scroll * self._CURVE_F1) * 0.85
            + math.sin(scroll * self._CURVE_F2 + 1.3) * 0.28
            + math.sin(scroll * self._CURVE_F3 + 2.7) * 0.08
        )

    def _compute_curve_scale(self) -> float:
        peak = 0.0
        for s in range(0, 50000, 5):
            peak = max(peak, abs(self._curve_raw(float(s))))
        return 1.0 / (peak ** self._CURVE_POW)

    def _curve_value(self, scroll: float) -> float:
        raw = self._curve_raw(scroll)
        return math.copysign(abs(raw) ** self._CURVE_POW * self._curve_scale, raw)

    def _car_yaw(self, scroll: float) -> float:
        cv = self._curve_value(scroll)
        if cv > 0.6:
            return self._CAR_YAW_HARD
        if cv > 0.2:
            return self._CAR_YAW_GENTLE
        if cv < -0.6:
            return -self._CAR_YAW_HARD
        if cv < -0.2:
            return -self._CAR_YAW_GENTLE
        return 0.0

    def _car_tilt(self, scroll: float) -> float:
        cv = self._curve_value(scroll)
        if cv > 0.6:
            return self._CAR_TILT_HARD
        if cv > 0.2:
            return self._CAR_TILT_GENTLE
        if cv < -0.6:
            return -self._CAR_TILT_HARD
        if cv < -0.2:
            return -self._CAR_TILT_GENTLE
        return 0.0

    def _project(self, pts: np.ndarray, scx: float, scy: float) -> np.ndarray:
        x = pts[:, 0]
        y = pts[:, 1]
        z = pts[:, 2]
        cz = np.maximum(z + self._CAR_CAM_D, 0.1)
        sx = scx + self._CAR_FOCAL * x / cz
        sy = scy - self._CAR_FOCAL * (y - self._CAR_CAM_Y) / cz
        return np.stack([sx, sy], axis=1)

    def _draw_car(
        self,
        frame: np.ndarray,
        w: int,
        h: int,
        car_x: int,
        palette: Palette,
        yaw_deg: float,
        tilt_deg: float,
    ) -> None:
        surf = pygame.Surface(
            (self._CAR_CANVAS_W, self._CAR_CANVAS_H), pygame.SRCALPHA
        )
        scx = self._CAR_CANVAS_W / 2.0
        scy = self._CAR_SCY

        pri = np.array(palette.primary, dtype=np.float32)
        sec = np.array(palette.secondary, dtype=np.float32)
        dim = np.array(palette.dim, dtype=np.float32)
        colors = {
            "body": pri,
            "side": pri * 0.7,
            "top": np.clip(pri * 0.55 + 70.0, 0, 255),
            "glass": dim * 0.45,
            "glass_side": dim * 0.6,
            "roof": sec,
            "tail": np.array([255.0, 60.0, 50.0], dtype=np.float32),
            "tire": np.array([18.0, 18.0, 18.0], dtype=np.float32),
        }

        a = math.radians(yaw_deg)
        ca, sa = math.cos(a), math.sin(a)

        def rot(pts: np.ndarray) -> np.ndarray:
            out = pts.copy()
            out[:, 0] = pts[:, 0] * ca + pts[:, 2] * sa
            out[:, 2] = -pts[:, 0] * sa + pts[:, 2] * ca
            return out

        # Body box
        HW, HL = 16.0, 24.0
        BY0, BY1 = 3.0, 13.0
        # Stable ground line: rear-wheel contact at yaw 0 (anchors vertical placement)
        rear_cz = self._CAR_CAM_D - (HL - 6.0)
        ground_ref = (
            self._CAR_SCY
            + self._CAR_FOCAL * self._CAR_CAM_Y / rear_cz
            + self._CAR_WHEEL_R_MAX
        )
        body = np.array(
            [
                [-HW, BY0, -HL], [HW, BY0, -HL], [HW, BY1, -HL], [-HW, BY1, -HL],
                [-HW, BY0, HL], [HW, BY0, HL], [HW, BY1, HL], [-HW, BY1, HL],
            ],
            dtype=np.float64,
        )
        # Cabin / greenhouse on top, set toward the rear
        CW, CZ0, CZ1 = 12.0, -12.0, 8.0
        CY0, CY1 = BY1, 20.0
        cabin = np.array(
            [
                [-CW, CY0, CZ0], [CW, CY0, CZ0], [CW, CY1, CZ0], [-CW, CY1, CZ0],
                [-CW, CY0, CZ1], [CW, CY0, CZ1], [CW, CY1, CZ1], [-CW, CY1, CZ1],
            ],
            dtype=np.float64,
        )
        body_r = rot(body)
        cabin_r = rot(cabin)
        bp = self._project(body_r, scx, scy)
        cp = self._project(cabin_r, scx, scy)
        bz = body_r[:, 2]
        czz = cabin_r[:, 2]

        # Painter's algorithm: farthest (largest z) first
        items: list[tuple[float, str, object]] = []

        def face(depth: float, idx: tuple[int, ...], verts: np.ndarray, color: np.ndarray) -> None:
            items.append((depth, "face", ([verts[i] for i in idx], color)))

        face(float(np.mean(bz[[0, 1, 2, 3]])), (0, 1, 2, 3), bp, colors["body"])
        face(float(np.mean(bz[[4, 5, 6, 7]])), (4, 5, 6, 7), bp, colors["body"])
        face(float(np.mean(bz[[0, 3, 7, 4]])), (0, 3, 7, 4), bp, colors["side"])
        face(float(np.mean(bz[[1, 2, 6, 5]])), (1, 2, 6, 5), bp, colors["side"])
        face(float(np.mean(bz[[3, 2, 6, 7]])), (3, 2, 6, 7), bp, colors["top"])
        face(float(np.mean(czz[[0, 1, 2, 3]])), (0, 1, 2, 3), cp, colors["glass"])
        face(float(np.mean(czz[[4, 5, 6, 7]])), (4, 5, 6, 7), cp, colors["glass"])
        face(float(np.mean(czz[[0, 3, 7, 4]])), (0, 3, 7, 4), cp, colors["glass_side"])
        face(float(np.mean(czz[[1, 2, 6, 5]])), (1, 2, 6, 5), cp, colors["glass_side"])
        face(float(np.mean(czz[[3, 2, 6, 7]])), (3, 2, 6, 7), cp, colors["roof"])

        # Wheels at the four corners, just outside the body
        for wsx in (-1.0, 1.0):
            for wsz in (-1.0, 1.0):
                wpt = rot(
                    np.array([[wsx * (HW + 1.0), 0.0, wsz * (HL - 6.0)]], dtype=np.float64)
                )
                wproj = self._project(wpt, scx, scy)[0]
                depth = float(wpt[0, 2])
                cz_w = max(depth + self._CAR_CAM_D, 0.1)
                r = min(
                    self._CAR_WHEEL_R_MAX, max(3, int(self._CAR_FOCAL * 4.5 / cz_w))
                )
                items.append((depth, "wheel", (wproj, r)))

        # Tail lights, just proud of the rear face (toward the camera)
        for ttx in (-HW * 0.62, HW * 0.62):
            tpt = rot(np.array([[ttx, BY0 + 2.5, -HL - 0.5]], dtype=np.float64))
            tproj = self._project(tpt, scx, scy)[0]
            depth = float(tpt[0, 2])
            cz_t = max(depth + self._CAR_CAM_D, 0.1)
            r = max(2, int(self._CAR_FOCAL * 2.2 / cz_t))
            items.append((depth, "tail", (tproj, r)))

        items.sort(key=lambda it: -it[0])

        for _, kind, payload in items:
            if kind == "face":
                verts, color = payload
                poly = [(float(v[0]), float(v[1])) for v in verts]
                pygame.draw.polygon(surf, _to_rgb(color), poly)
            elif kind == "wheel":
                (cxw, cyw), rr = payload
                pygame.draw.circle(surf, _to_rgb(colors["tire"]), (int(cxw), int(cyw)), rr)
            elif kind == "tail":
                (cxt, cyt), rr = payload
                pygame.draw.circle(surf, _to_rgb(colors["tail"]), (int(cxt), int(cyt)), rr)

        if abs(tilt_deg) > 0.01:
            surf = pygame.transform.rotate(surf, tilt_deg)

        # Alpha-blend the car sprite into the numpy frame
        arr3 = pygame.surfarray.array3d(surf).transpose(1, 0, 2).astype(np.float32)
        alpha = (
            pygame.surfarray.array_alpha(surf).transpose(1, 0).astype(np.float32) / 255.0
        )
        ch2, cw2 = arr3.shape[:2]
        x0 = car_x - cw2 // 2
        y0 = (h - 1) - int(round(ground_ref))
        gx, gy = np.meshgrid(np.arange(cw2) + x0, np.arange(ch2) + y0)
        valid = (gx >= 0) & (gx < w) & (gy >= 0) & (gy < h) & (alpha > 0.0)
        iy, ix = np.where(valid)
        if iy.size:
            a_ = alpha[iy, ix][:, None]
            frame[gy[iy, ix], gx[iy, ix]] = (
                frame[gy[iy, ix], gx[iy, ix]] * (1.0 - a_) + arr3[iy, ix] * a_
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

        # Car - 3D box-car that yaws into curves, with a subtle lean
        self._draw_car(
            frame,
            w,
            h,
            car_x,
            palette,
            self._car_yaw(scroll),
            self._car_tilt(scroll),
        )

        return np.clip(frame, 0, 255).astype(np.uint8)


outrun = _OutrunEffect()
