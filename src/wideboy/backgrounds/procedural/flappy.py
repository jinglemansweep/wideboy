from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import draw_obj


class _FlappyEffect(Effect):
    name = "flappy"
    default_palette = "neon"
    tags = ("game", "retro")

    _GRAVITY = 1500.0
    _FLAP_VEL = -178.0
    _MAX_FALL = 460.0
    _BIRD_X = 90
    _BIRD_W = 8
    _BIRD_H = 6
    _PIPE_W = 26
    _PIPE_GAP_H = 28
    _PIPE_SPEED = 88.0
    _PIPE_SPACING = 232
    _PIPE_MARGIN = 6
    _PIPE_MAX_DELTA = 16
    _DEATH_FREEZE = 1.0
    _SIM_HZ = 120.0

    _AI_FLAP_GUARD = -30.0
    _WANDER_RANGE = 7.0
    _WANDER_INTERVAL_MIN = 0.25
    _WANDER_INTERVAL_MAX = 0.7
    _WANDER_STEP = 3.5
    _FLAP_MARGIN = 2.5
    _FLAP_FACTOR_MIN = 0.65
    _STRAY_FLAP_RATE = 0.9
    _LAPSE_MIN = 7.0
    _LAPSE_MAX = 16.0
    _LAPSE_DUR_MIN = 0.25
    _LAPSE_DUR_MAX = 0.55
    _N_PARTICLES = 14

    _BIRD_UP = np.array(
        [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 4, 1, 1, 3, 3],
            [2, 1, 1, 1, 1, 1, 3, 0],
            [2, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
        ],
        dtype=np.int8,
    )
    _BIRD_DOWN = np.array(
        [
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 4, 1, 1, 3, 3],
            [0, 1, 1, 1, 1, 1, 3, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 0, 0, 0],
            [2, 2, 0, 1, 1, 0, 0, 0],
        ],
        dtype=np.int8,
    )

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._prev_t = -1.0
        self._rng = np.random.RandomState(42)
        self._bird_y = 0.0
        self._bird_vy = 0.0
        self._pipes: list[dict] = []
        self._particles: list[dict] = []
        self._alive = True
        self._death_t = 0.0
        self._in_lapse = False
        self._lapse_timer = 0.0
        self._lapse_remaining = 0.0
        self._wander = 0.0
        self._wander_timer = 0.0

    def _gap_range(self) -> tuple[float, float]:
        lo = self._PIPE_MARGIN + self._PIPE_GAP_H / 2
        hi = self._h - self._PIPE_MARGIN - self._PIPE_GAP_H / 2
        return lo, hi

    def _spawn_pipe(self) -> None:
        lo, hi = self._gap_range()
        if self._pipes:
            prev = self._pipes[-1]["gap_center"]
            clo = max(lo, prev - self._PIPE_MAX_DELTA)
            chi = min(hi, prev + self._PIPE_MAX_DELTA)
        else:
            clo, chi = lo, hi
        center = self._rng.uniform(clo, chi)
        self._pipes.append({"x": float(self._w + 4), "gap_center": center})

    def _flap(self, gap_top: float | None) -> None:
        if gap_top is not None:
            room = max(0.0, self._bird_y - gap_top - self._FLAP_MARGIN)
            v_max = math.sqrt(2.0 * self._GRAVITY * room)
        else:
            v_max = abs(self._FLAP_VEL)
        base = min(abs(self._FLAP_VEL), v_max)
        factor = self._rng.uniform(self._FLAP_FACTOR_MIN, 1.0)
        self._bird_vy = -base * factor

    def _update_wander(self, dt: float) -> None:
        self._wander_timer -= dt
        if self._wander_timer <= 0.0:
            self._wander += self._rng.uniform(-self._WANDER_STEP, self._WANDER_STEP)
            self._wander = max(-self._WANDER_RANGE, min(self._WANDER_RANGE, self._wander))
            self._wander_timer = self._rng.uniform(
                self._WANDER_INTERVAL_MIN, self._WANDER_INTERVAL_MAX
            )

    def _stray_flap(self, sub_dt: float) -> bool:
        return self._rng.random() < self._STRAY_FLAP_RATE * sub_dt

    def _schedule_lapse(self) -> None:
        self._lapse_timer = self._rng.uniform(self._LAPSE_MIN, self._LAPSE_MAX)

    def _die(self, palette: Palette) -> None:
        if not self._alive:
            return
        self._alive = False
        self._death_t = 0.0
        self._in_lapse = False
        acc = np.array(palette.accent, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        cx = self._BIRD_X + self._BIRD_W / 2
        cy = self._bird_y + self._BIRD_H / 2
        for _ in range(self._N_PARTICLES):
            ang = self._rng.uniform(0.0, 2.0 * np.pi)
            spd = self._rng.uniform(40.0, 150.0)
            self._particles.append(
                {
                    "x": cx,
                    "y": cy,
                    "vx": np.cos(ang) * spd,
                    "vy": np.sin(ang) * spd - 60.0,
                    "life": self._rng.uniform(0.4, 0.9),
                    "max_life": 0.9,
                    "color": hi if self._rng.random() < 0.5 else acc,
                }
            )

    def _reset(self) -> None:
        self._bird_y = self._h / 2 - self._BIRD_H / 2
        self._bird_vy = 0.0
        self._pipes = [{"x": float(self._w * 0.55), "gap_center": self._h / 2}]
        self._particles = []
        self._alive = True
        self._death_t = 0.0
        self._in_lapse = False
        self._wander = 0.0
        self._wander_timer = 0.0
        self._schedule_lapse()

    def _init(self, w: int, h: int) -> None:
        self._w = w
        self._h = h
        self._reset()

    def _ai_should_flap(self, pipe: dict | None) -> bool:
        if self._in_lapse:
            return False
        target = (pipe["gap_center"] + self._wander) if pipe else self._h / 2
        bird_center = self._bird_y + self._BIRD_H / 2
        return bird_center >= target and self._bird_vy > self._AI_FLAP_GUARD

    def _collided(self) -> bool:
        bx0 = self._BIRD_X
        bx1 = self._BIRD_X + self._BIRD_W
        by0 = self._bird_y
        by1 = self._bird_y + self._BIRD_H
        if by1 >= self._h:
            return True
        for p in self._pipes:
            if p["x"] + self._PIPE_W <= bx0 or p["x"] >= bx1:
                continue
            gap_top = p["gap_center"] - self._PIPE_GAP_H / 2
            gap_bottom = p["gap_center"] + self._PIPE_GAP_H / 2
            if by0 < gap_top or by1 > gap_bottom:
                return True
        return False

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h:
            self._init(w, h)

        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        dt = min(dt, 0.05)
        self._prev_t = t

        dim = np.array(palette.dim, dtype=np.uint8)
        pri = np.array(palette.primary, dtype=np.uint8)
        sec = np.array(palette.secondary, dtype=np.uint8)
        acc = np.array(palette.accent, dtype=np.uint8)
        hi = np.array(palette.highlight, dtype=np.uint8)

        if self._alive:
            self._lapse_timer -= dt
            if not self._in_lapse and self._lapse_timer <= 0.0:
                self._in_lapse = True
                self._lapse_remaining = self._rng.uniform(self._LAPSE_DUR_MIN, self._LAPSE_DUR_MAX)
            elif self._in_lapse:
                self._lapse_remaining -= dt
                if self._lapse_remaining <= 0.0:
                    self._in_lapse = False
                    self._schedule_lapse()

            for p in self._pipes:
                p["x"] -= self._PIPE_SPEED * dt
            if not self._pipes or self._pipes[-1]["x"] < self._w - self._PIPE_SPACING:
                self._spawn_pipe()
            self._pipes = [p for p in self._pipes if p["x"] + self._PIPE_W > -2]

            self._update_wander(dt)

            sub_steps = max(1, math.ceil(dt * self._SIM_HZ))
            sub_dt = dt / sub_steps
            for _ in range(sub_steps):
                pipe = None
                for p in self._pipes:
                    if p["x"] + self._PIPE_W > self._BIRD_X:
                        pipe = p
                        break
                gap_top = (pipe["gap_center"] - self._PIPE_GAP_H / 2) if pipe else None
                if self._ai_should_flap(pipe) or self._stray_flap(sub_dt):
                    self._flap(gap_top)
                self._bird_vy = min(self._bird_vy + self._GRAVITY * sub_dt, self._MAX_FALL)
                self._bird_y += self._bird_vy * sub_dt
                if self._bird_y < 0.0:
                    self._bird_y = 0.0
                    self._bird_vy = max(self._bird_vy, 0.0)
                if self._collided():
                    self._die(palette)
                    break
        else:
            self._death_t += dt
            self._bird_vy = min(self._bird_vy + self._GRAVITY * dt, self._MAX_FALL)
            self._bird_y += self._bird_vy * dt
            if self._bird_y + self._BIRD_H > self._h:
                self._bird_y = self._h - self._BIRD_H
                self._bird_vy = 0.0
            if self._death_t >= self._DEATH_FREEZE:
                self._reset()

        for pt in self._particles:
            pt["x"] += pt["vx"] * dt
            pt["y"] += pt["vy"] * dt
            pt["vy"] += self._GRAVITY * 0.6 * dt
            pt["life"] -= dt
        self._particles = [pt for pt in self._particles if pt["life"] > 0.0]

        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim

        ground_y = h - 2
        if 0 <= ground_y < h:
            frame[ground_y, :] = sec

        for p in self._pipes:
            px0 = max(0, int(p["x"]))
            px1 = min(w, int(p["x"] + self._PIPE_W))
            if px1 <= px0:
                continue
            gap_top = p["gap_center"] - self._PIPE_GAP_H / 2
            gap_bottom = p["gap_center"] + self._PIPE_GAP_H / 2
            top_y0 = 0
            top_y1 = max(0, int(gap_top))
            bot_y0 = min(h, int(gap_bottom))
            bot_y1 = h
            if top_y1 > top_y0:
                frame[top_y0:top_y1, px0:px1] = pri
                lip = max(0, top_y1 - 2)
                frame[lip:top_y1, px0:px1] = sec
            if bot_y1 > bot_y0:
                frame[bot_y0:bot_y1, px0:px1] = pri
                lip = min(h, bot_y0 + 2)
                frame[bot_y0:lip, px0:px1] = sec

        sprite = self._BIRD_UP if self._bird_vy < -40.0 else self._BIRD_DOWN
        colors = [dim, hi, sec, acc, dim]
        draw_obj(frame, sprite, self._BIRD_X, int(self._bird_y), colors, h)

        for pt in self._particles:
            r = max(0.0, min(1.0, pt["life"] / pt["max_life"]))
            c = (pt["color"] * r + dim * (1.0 - r)).astype(np.uint8)
            px = int(pt["x"])
            py = int(pt["y"])
            if 0 <= px < w and 0 <= py < h:
                frame[py, px] = c

        return frame


flappy = _FlappyEffect()
