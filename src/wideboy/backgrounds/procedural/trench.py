from __future__ import annotations

import math

import numpy as np
import pygame

from ...render.palette import Palette
from ._base import Effect


class _TrenchEffect(Effect):
    name = "trench"
    default_palette = "mono"
    tags = ("game", "retro", "nostalgic", "energetic")

    _HORIZON = 30
    _FOCAL_X = 55.0
    _FOCAL_Y = 18.0
    _CAM_H = 0.5
    _WALL_TOP = 1.8
    _T = 1.0

    _FLOOR_DENS = 1.1
    _RUNG_W = 0.07
    _RIB_DENS = 5.0
    _RIB_W = 0.10
    _RIB_GROOVE = 0.07
    _DECK_PERIOD = 0.6

    _WORLD_SPEED = 2.5
    _RECYCLE_RANGE = 12.0
    _NEAR_CLIP = 0.18
    _N_STARS = 46

    _N_OBSTACLES = 8
    _PROTR_MIN = 0.24
    _PROTR_MAX = 0.48
    _BARREL_PROB = 0.55
    _BARREL_LEN_MIN = 0.18
    _BARREL_LEN_MAX = 0.36
    _BARREL_Y = 0.42

    _SHIP_STIFF = 16.0
    _SHIP_DAMP = 7.0
    _SHIP_WANDER_RATE = 1.4
    _SHIP_WANDER_DECAY = 0.9
    _SHIP_WANDER_RANGE = 0.55
    _SHIP_BANK_K = 7.0
    _SHIP_BANK_MAX = 14.0
    _SHIP_SCALE = 1.1
    _SHIP_BOTTOM_PAD = 2
    _SHIP_VWANDER_RATE = 1.0
    _SHIP_VWANDER_RANGE = 2.2

    _LASER_RATE_MIN = 0.22
    _LASER_RATE_MAX = 0.6
    _LASER_SPEED_MIN = 1.8
    _LASER_SPEED_MAX = 2.6
    _LASER_TAIL = 30.0
    _LASER_GREEN = (40.0, 255.0, 130.0)
    _LASER_RED = (255.0, 75.0, 55.0)

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._zw_bottom = 0.0
        self._ship_x_range = 200.0
        self._last_t: float | None = None
        self._scroll = 0.0
        self._obj_scroll = 0.0
        self._obstacles: list[dict] = []
        self._stars: list[tuple[int, int, float, float]] = []
        self._ship_pos = 0.0
        self._ship_vel = 0.0
        self._wander = 0.0
        self._v_wander = 0.0
        self._wander_rng = np.random.RandomState(2024)
        self._reroll = np.random.RandomState(123)
        self._lasers: list[dict] = []
        self._laser_timer = 0.0
        self._laser_rng = np.random.RandomState(99)
        self._cache: dict[str, np.ndarray] = {}

    def _spawn_obstacle(self, rng: np.random.RandomState, world_z: float) -> dict:
        return {
            "type": "turret",
            "world_z": world_z,
            "side": int(rng.choice([-1, 1])),
            "protr": float(rng.uniform(self._PROTR_MIN, self._PROTR_MAX)),
            "barrel": float(
                rng.uniform(self._BARREL_LEN_MIN, self._BARREL_LEN_MAX)
            )
            if rng.random() < self._BARREL_PROB
            else 0.0,
        }

    def _init(self, w: int, h: int) -> None:
        self._w, self._h = w, h
        horizon = self._HORIZON
        cx = w / 2.0
        span = float(h - 1 - horizon)
        self._zw_bottom = self._FOCAL_Y * self._CAM_H / max(span, 1.0)
        self._ship_x_range = self._FOCAL_X / self._zw_bottom

        py = np.arange(h, dtype=np.float32)[:, None]
        px = np.arange(w, dtype=np.float32)[None, :]
        dy = py - horizon
        dx = px - cx

        zw_f = np.where(dy > 0, self._FOCAL_Y * self._CAM_H / np.maximum(dy, 1e-3), 1e9).astype(
            np.float32
        )
        xw_f = (dx * zw_f / self._FOCAL_X).astype(np.float32)
        floor_mask = ((dy > 0) & (np.abs(xw_f) <= self._T)).astype(bool)

        ad = np.abs(dx)
        zw_w = (self._FOCAL_X * self._T / np.maximum(ad, 1e-3)).astype(np.float32)
        yw_w = (self._CAM_H - dy * zw_w / self._FOCAL_Y).astype(np.float32)
        wall_valid = (
            (yw_w >= 0.0)
            & (yw_w <= self._WALL_TOP)
            & (zw_w > 0.0)
            & (zw_w < 30.0)
        )
        wall_mask = (wall_valid & ~floor_mask).astype(bool)
        sky_mask = (~floor_mask & ~wall_mask).astype(bool)

        sky_top = np.array([4.0, 5.0, 10.0], dtype=np.float32)
        sky_hor = np.array([14.0, 16.0, 26.0], dtype=np.float32)
        tt = np.clip(py / max(horizon, 1), 0.0, 1.0).astype(np.float32)
        tt3 = tt[:, :, None]
        sky_row = (sky_top * (1 - tt3) + sky_hor * tt3).astype(np.float32)

        ex = np.arange(w, dtype=np.float32)
        ed = np.minimum(ex, w - 1 - ex)
        edge_mul = (0.4 + 0.6 * np.clip(ed / 26.0, 0.0, 1.0)).astype(np.float32)

        rng = np.random.RandomState(7)
        self._obstacles = []
        spacing = self._RECYCLE_RANGE / self._N_OBSTACLES
        for i in range(self._N_OBSTACLES):
            ob = self._spawn_obstacle(rng, i * spacing)
            ob["_prev"] = None
            self._obstacles.append(ob)
        self._stars = []
        for _ in range(self._N_STARS):
            self._stars.append(
                (
                    int(rng.randint(0, w)),
                    int(rng.randint(0, max(1, horizon + 6))),
                    float(rng.uniform(0.35, 1.0)),
                    float(rng.uniform(0.0, math.tau)),
                )
            )
        self._ship_pos = 0.0
        self._ship_vel = 0.0
        self._wander = 0.0
        self._v_wander = 0.0
        self._lasers = []
        self._laser_timer = 0.0

        self._cache = {
            "cx": np.float32(cx),
            "zw_f": zw_f,
            "xw_f": xw_f,
            "zw_w": zw_w,
            "yw_w": yw_w,
            "floor_mask": floor_mask,
            "wall_mask": wall_mask,
            "sky_mask": sky_mask,
            "sky_row": sky_row,
            "edge_mul": edge_mul,
        }

    @staticmethod
    def _fill(
        frame: np.ndarray,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        color: np.ndarray,
        w: int,
        h: int,
    ) -> None:
        ix0 = max(0, int(math.floor(min(x0, x1))))
        ix1 = min(w, int(math.ceil(max(x0, x1))))
        iy0 = max(0, int(math.floor(min(y0, y1))))
        iy1 = min(h, int(math.ceil(max(y0, y1))))
        if ix1 > ix0 and iy1 > iy0:
            frame[iy0:iy1, ix0:ix1] = color

    @staticmethod
    def _edge_h(
        frame: np.ndarray, y: float, x0: float, x1: float,
        color: np.ndarray, w: int, h: int,
    ) -> None:
        iy = int(round(y))
        if not (0 <= iy < h):
            return
        ix0 = max(0, int(math.floor(min(x0, x1))))
        ix1 = min(w, int(math.ceil(max(x0, x1))))
        if ix1 > ix0:
            frame[iy, ix0:ix1] = np.maximum(frame[iy, ix0:ix1], color)

    @staticmethod
    def _edge_v(
        frame: np.ndarray, x: float, y0: float, y1: float,
        color: np.ndarray, w: int, h: int,
    ) -> None:
        ix = int(round(x))
        if not (0 <= ix < w):
            return
        iy0 = max(0, int(math.floor(min(y0, y1))))
        iy1 = min(h, int(math.ceil(max(y0, y1))))
        if iy1 > iy0:
            frame[iy0:iy1, ix] = np.maximum(frame[iy0:iy1, ix], color)

    def _pt(
        self, frame: np.ndarray, x: int, y: int, color: np.ndarray, w: int, h: int
    ) -> None:
        if 0 <= x < w and 0 <= y < h:
            frame[y, x] = np.maximum(frame[y, x], color)

    def _draw_ship(
        self,
        frame: np.ndarray,
        cx_s: float,
        cy_s: float,
        palette: Palette,
        bank_deg: float,
        bob: float,
        t: float,
        w: int,
        h: int,
    ) -> None:
        SW, SH = 46, 38
        surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        ox, oy = SW / 2.0, SH / 2.0

        pri = np.array(palette.primary, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        dim = np.array(palette.dim, dtype=np.float32)

        def rgb(c: np.ndarray) -> tuple[int, int, int]:
            return (
                int(max(0.0, min(255.0, c[0]))),
                int(max(0.0, min(255.0, c[1]))),
                int(max(0.0, min(255.0, c[2]))),
            )

        lit = rgb(np.clip(pri * 0.55 + hi * 0.5, 0, 255))
        body = rgb(pri)
        body_sh = rgb(pri * 0.78)
        dark = rgb(pri * 0.45)
        very_dark = rgb(pri * 0.25 + dim * 0.2)
        glass = rgb(np.clip(dim * 0.7 + pri * 0.15, 0, 255))

        def P(x: float, y: float) -> tuple[float, float]:
            return (x + ox, y + oy)

        pygame.draw.polygon(
            surf, dark, [P(-3, 1), P(-3, 8), P(-17, 11), P(-18, 4)]
        )
        pygame.draw.polygon(
            surf, dark, [P(3, 1), P(3, 8), P(17, 11), P(18, 4)]
        )
        pygame.draw.polygon(
            surf, body_sh, [P(-3, -10), P(-3, -3), P(-17, -11), P(-18, -5)]
        )
        pygame.draw.polygon(
            surf, body_sh, [P(3, -10), P(3, -3), P(17, -11), P(18, -5)]
        )
        pygame.draw.polygon(
            surf, very_dark, [P(-18, -5), P(-18, 4), P(-20, 4), P(-20, -5)]
        )
        pygame.draw.polygon(
            surf, very_dark, [P(18, -5), P(18, 4), P(20, 4), P(20, -5)]
        )
        pygame.draw.polygon(
            surf,
            body,
            [
                P(0, -16), P(2, -11), P(4, -2), P(4, 7), P(2, 13),
                P(0, 15), P(-2, 13), P(-4, 7), P(-4, -2), P(-2, -11),
            ],
        )
        pygame.draw.polygon(
            surf, lit, [P(0, -16), P(1, -8), P(1, 8), P(0, 14), P(-1, 8), P(-1, -8)]
        )
        pygame.draw.polygon(surf, glass, [P(-2, -9), P(2, -9), P(1, -4), P(-1, -4)])
        pygame.draw.line(surf, dark, P(-3, -3), P(-17, -8), 1)
        pygame.draw.line(surf, dark, P(3, -3), P(17, -8), 1)
        pygame.draw.line(surf, dark, P(-3, 2), P(-17, 7), 1)
        pygame.draw.line(surf, dark, P(3, 2), P(17, 7), 1)

        flick = 0.7 + 0.3 * math.sin(t * 26.0)
        eng = rgb(np.clip(acc * (0.7 + 0.3 * flick), 0, 255))
        eng_hot = rgb(np.clip(acc * 0.4 + hi * 0.6, 0, 255))
        eng_dim = rgb(np.clip(acc * 0.45, 0, 255))
        for ex, ey, r in ((-12, 8, 2), (12, 8, 2), (-6, 13, 2), (6, 13, 2)):
            pygame.draw.circle(surf, eng_dim, P(ex, ey), r + 1)
            pygame.draw.circle(surf, eng, P(ex, ey), r)
            pygame.draw.circle(surf, eng_hot, P(ex, ey), max(1, r - 1))
        for tx in (-3, 3):
            pygame.draw.line(surf, eng_dim, P(tx, 14), P(tx, 17), 1)

        scale = self._SHIP_SCALE
        surf = pygame.transform.smoothscale(
            surf, (max(1, int(SW * scale)), max(1, int(SH * scale)))
        )
        if abs(bank_deg) > 0.05:
            surf = pygame.transform.rotate(surf, bank_deg)

        arr3 = pygame.surfarray.array3d(surf).transpose(1, 0, 2).astype(np.float32)
        alpha = pygame.surfarray.array_alpha(surf).transpose(1, 0).astype(np.float32) / 255.0
        ch, cw = arr3.shape[:2]
        x0 = int(round(cx_s - cw / 2.0))
        y0 = h - 1 - ch - self._SHIP_BOTTOM_PAD - int(round(bob))
        gx, gy = np.meshgrid(np.arange(cw) + x0, np.arange(ch) + y0)
        valid = (gx >= 0) & (gx < w) & (gy >= 0) & (gy < h) & (alpha > 0.0)
        iy, ix = np.where(valid)
        if iy.size:
            a = alpha[iy, ix][:, None]
            frame[gy[iy, ix], gx[iy, ix]] = (
                frame[gy[iy, ix], gx[iy, ix]] * (1.0 - a) + arr3[iy, ix] * a
            )

    def _spawn_laser(
        self, w: int, h: int, cx: float, horizon: int, ship_x: float
    ) -> None:
        if ship_x - cx > 0.12 * self._ship_x_range:
            side = -1
        elif ship_x - cx < -0.12 * self._ship_x_range:
            side = 1
        else:
            side = int(self._laser_rng.choice([-1, 1]))
        sx0 = cx + side * float(self._laser_rng.uniform(55, 240))
        sy0 = h + 6
        ex = cx + side * float(self._laser_rng.uniform(15, 75))
        ey = horizon + float(self._laser_rng.uniform(-2, 10))
        color = self._LASER_GREEN if self._laser_rng.random() < 0.5 else self._LASER_RED
        speed = float(self._laser_rng.uniform(self._LASER_SPEED_MIN, self._LASER_SPEED_MAX))
        self._lasers.append(
            {"sx0": sx0, "sy0": sy0, "ex": ex, "ey": ey, "p": 0.0, "speed": speed, "color": color}
        )

    def _draw_laser(self, frame: np.ndarray, L: dict, w: int, h: int) -> None:
        p = L["p"]
        fade = max(0.0, 1.0 - 0.5 * p)
        hx = L["sx0"] + (L["ex"] - L["sx0"]) * p
        hy = L["sy0"] + (L["ey"] - L["sy0"]) * p
        dxv = L["ex"] - L["sx0"]
        dyv = L["ey"] - L["sy0"]
        ln = math.hypot(dxv, dyv)
        if ln < 1e-3:
            return
        ux = dxv / ln
        uy = dyv / ln
        tail = self._LASER_TAIL * (1.0 - 0.45 * p)
        base = np.array(L["color"], dtype=np.float32) * fade
        px_perp_x = uy
        px_perp_y = -ux
        s = 0.0
        while s < tail:
            f = s / tail
            cxp = hx - ux * s
            cyp = hy - uy * s
            core = base * (0.35 + 0.65 * (1.0 - f))
            self._pt(frame, int(cxp), int(cyp), core, w, h)
            self._pt(frame, int(cxp + px_perp_x), int(cyp + px_perp_y), core * 0.7, w, h)
            self._pt(frame, int(cxp - px_perp_x), int(cyp - px_perp_y), core * 0.7, w, h)
            s += 0.6
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                self._pt(frame, int(hx) + ox, int(hy) + oy, base, w, h)

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h:
            self._init(w, h)

        if self._last_t is None:
            self._last_t = t
        dt = max(0.0, min(0.05, t - self._last_t))
        self._last_t = t
        self._scroll += dt * self._WORLD_SPEED
        self._obj_scroll += dt * self._WORLD_SPEED

        dim = np.array(palette.dim, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        acc = np.array(palette.accent, dtype=np.float32)

        c = self._cache
        cx = float(c["cx"])
        zw_f = c["zw_f"]
        xw_f = c["xw_f"]
        yw_w = c["yw_w"]
        floor_mask = c["floor_mask"]
        sky_mask = c["sky_mask"]
        sky_row = c["sky_row"]
        scroll = self._scroll

        floor_dark = np.array([14.0, 16.0, 20.0], dtype=np.float32)
        floor_light = np.array([46.0, 50.0, 60.0], dtype=np.float32)
        rail_c = np.array([82.0, 90.0, 108.0], dtype=np.float32)
        wall_low = np.array([72.0, 78.0, 92.0], dtype=np.float32)
        wall_high = np.array([20.0, 24.0, 32.0], dtype=np.float32)
        rib_line = np.array([22.0, 25.0, 34.0], dtype=np.float32)
        rib_bevel = np.array([50.0, 55.0, 68.0], dtype=np.float32)
        deck_c = np.array([44.0, 49.0, 60.0], dtype=np.float32)

        rung = (((zw_f + scroll) * self._FLOOR_DENS) % 1.0) < self._RUNG_W
        floor_color = np.where(rung[..., None], floor_light, floor_dark)
        ax = np.abs(xw_f)
        rail = (ax < 0.02) | (np.abs(ax % 0.34) < 0.02)
        floor_color = np.where(rail[..., None], rail_c, floor_color)

        zw_w = c["zw_w"]
        rib_phase = ((zw_w + scroll) * self._RIB_DENS) % 1.0
        rib = rib_phase < self._RIB_W
        groove = (rib_phase >= self._RIB_W) & (rib_phase < self._RIB_W + self._RIB_GROOVE)
        hf = np.clip(yw_w / self._WALL_TOP, 0.0, 1.0)
        wall_base = wall_low * (1 - hf[..., None]) + wall_high * hf[..., None]
        wall_color = np.where(groove[..., None], rib_bevel, wall_base)
        wall_color = np.where(rib[..., None], rib_line, wall_color)
        deck = (yw_w % self._DECK_PERIOD) < 0.03
        wall_color = np.where(deck[..., None], deck_c, wall_color)

        frame = np.where(
            sky_mask[..., None],
            sky_row,
            np.where(floor_mask[..., None], floor_color, wall_color),
        )

        star_c = hi
        for sx, sy, sb, sph in self._stars:
            if sky_mask[sy, sx]:
                b = sb * (0.5 + 0.5 * math.sin(t * 3.0 + sph))
                frame[sy, sx] = np.maximum(frame[sy, sx], dim * (1 - b) + star_c * b)

        frame *= c["edge_mul"][None, :, None]

        def SX(xw: float, zw: float) -> float:
            return cx + self._FOCAL_X * xw / zw

        def SY(yw: float, zw: float) -> float:
            return self._HORIZON + self._FOCAL_Y * (self._CAM_H - yw) / zw

        metal = np.array([104.0, 112.0, 128.0], dtype=np.float32)
        metal_dark = np.array([58.0, 64.0, 76.0], dtype=np.float32)
        metal_edge = np.array([185.0, 195.0, 210.0], dtype=np.float32)

        for ob in self._obstacles:
            cz = (ob["world_z"] - self._obj_scroll) % self._RECYCLE_RANGE + self._NEAR_CLIP
            prev = ob.get("_prev")
            if prev is not None and prev < 0.4 and cz > self._RECYCLE_RANGE * 0.5:
                for k in ("type", "side", "protr", "barrel"):
                    ob.pop(k, None)
                tmp = self._spawn_obstacle(self._reroll, ob["world_z"])
                ob.update({k: v for k, v in tmp.items() if k != "world_z"})
            ob["_prev"] = cz
            ob["_cz"] = cz
            ob["_scale"] = self._zw_bottom / cz

        for ob in sorted(self._obstacles, key=lambda o: o["_scale"]):
            s = ob["_scale"]
            if s < 0.04 or s > 1.3:
                continue
            cz = ob["_cz"]
            bright = min(1.0, 0.35 + s * 1.1)
            col = metal * bright
            col_d = metal_dark * bright
            col_e = metal_edge * bright

            sgn = ob["side"]
            protr = ob["protr"]
            bl = ob["barrel"]
            x_wall = sgn * self._T
            x_inner = sgn * (self._T - protr)
            sx_inner = SX(x_inner, cz)
            sx_wall = SX(x_wall, cz)
            sy_top = SY(self._WALL_TOP, cz)
            sy_bot = SY(0.0, cz)
            self._fill(frame, sx_inner, sy_top, sx_wall, sy_bot, col, w, h)
            for fxw in (0.33, 0.66):
                xv = SX(sgn * (self._T - protr * fxw), cz)
                self._edge_v(frame, xv, sy_top, sy_bot, col_d, w, h)
            for fyw in (self._WALL_TOP * 0.35, self._WALL_TOP * 0.7):
                self._edge_h(frame, SY(fyw, cz), sx_inner, sx_wall, col_d, w, h)
            self._edge_v(frame, sx_inner, sy_top, sy_bot, col_e, w, h)
            self._edge_h(frame, sy_bot - 1, sx_inner, sx_wall, col_e, w, h)
            if bl > 0.0:
                sy_bar = SY(self._BARREL_Y, cz)
                x_tip = sgn * (self._T - protr - bl)
                sx_tip = SX(x_tip, cz)
                thick = max(1.0, s * 2.2)
                x0b, x1b = (sx_tip, sx_inner) if sgn < 0 else (sx_inner, sx_tip)
                self._fill(
                    frame, x0b, sy_bar - thick, x1b, sy_bar + thick, acc * bright, w, h
                )
                self._pt(frame, int(round(sx_tip)), int(round(sy_bar)), hi, w, h)

        push = 0.0
        for ob in self._obstacles:
            s = ob["_scale"]
            if 0.1 <= s <= 1.2:
                strength = ((s - 0.1) / 1.1) ** 1.4
                push += -ob["side"] * strength
        desired = max(-1.0, min(1.0, push))
        self._wander += float(self._wander_rng.uniform(-1.0, 1.0)) * dt * self._SHIP_WANDER_RATE
        self._wander *= max(0.0, 1.0 - dt * self._SHIP_WANDER_DECAY)
        self._wander = max(-self._SHIP_WANDER_RANGE, min(self._SHIP_WANDER_RANGE, self._wander))
        self._v_wander += float(self._wander_rng.uniform(-1.0, 1.0)) * dt * self._SHIP_VWANDER_RATE
        self._v_wander *= max(0.0, 1.0 - dt * 0.8)
        self._v_wander = max(
            -self._SHIP_VWANDER_RANGE, min(self._SHIP_VWANDER_RANGE, self._v_wander)
        )
        target = max(-1.0, min(1.0, desired + self._wander * 0.45))
        accel = (target - self._ship_pos) * self._SHIP_STIFF - self._ship_vel * self._SHIP_DAMP
        self._ship_vel += accel * dt
        self._ship_pos = max(-1.0, min(1.0, self._ship_pos + self._ship_vel * dt))

        ship_sx = cx + self._ship_pos * self._ship_x_range
        ship_sy = h - 1 - self._SHIP_BOTTOM_PAD

        self._laser_timer -= dt
        if self._laser_timer <= 0.0:
            self._spawn_laser(w, h, cx, self._HORIZON, ship_sx)
            self._laser_timer = float(
                self._laser_rng.uniform(self._LASER_RATE_MIN, self._LASER_RATE_MAX)
            )
        for L in self._lasers:
            L["p"] += L["speed"] * dt
        self._lasers = [L for L in self._lasers if L["p"] < 1.05]
        for L in self._lasers:
            self._draw_laser(frame, L, w, h)

        bank = max(
            -self._SHIP_BANK_MAX, min(self._SHIP_BANK_MAX, -self._ship_vel * self._SHIP_BANK_K)
        )
        raw_bob = (
            math.sin(t * 1.6) * 2.6 + math.sin(t * 0.7 + 2.1) * 1.6 + self._v_wander
        )
        bob = max(-2.0, min(6.0, raw_bob + 1.5))
        self._draw_ship(frame, ship_sx, ship_sy, palette, bank, bob, t, w, h)

        return np.clip(frame, 0, 255).astype(np.uint8)


trench = _TrenchEffect()
