from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import draw_filled_wrapped_polygon, draw_wrapped_polygon


class _AsteroidsEffect(Effect):
    name = "asteroids"
    default_palette = "mono"
    tags = ("game", "retro", "energetic")

    _N_ROCKS = 10
    _SHIP_SIZE = 8
    _BULLET_SPEED = 300.0
    _BULLET_LIFE = 1.5
    _FIRE_INTERVAL = 0.8
    _SHIP_SPEED = 80.0
    _ROCK_SPEED_MIN = 15.0
    _ROCK_SPEED_MAX = 40.0

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._prev_t = -1.0
        self._rng = np.random.RandomState(42)
        self._rocks: list[dict] = []
        self._bullets: list[dict] = []
        self._particles: list[dict] = []
        self._ship_x = 0.0
        self._ship_y = 0.0
        self._ship_angle = 0.0
        self._ship_vx = 0.0
        self._ship_vy = 0.0
        self._fire_timer = 0.0
        self._target_angle = 0.0
        self._retarget_timer = 0.0
        self._init_state()

    def _init_state(self) -> None:
        self._rocks = []
        for _ in range(self._N_ROCKS):
            self._spawn_rock(size=3)
        self._bullets = []
        self._particles = []
        self._ship_x = self._w / 2
        self._ship_y = self._h / 2
        self._ship_angle = self._rng.uniform(0, 2 * math.pi)
        self._ship_vx = 0.0
        self._ship_vy = 0.0
        self._fire_timer = 0.0
        self._target_angle = self._rng.uniform(0, 2 * math.pi)
        self._retarget_timer = 0.0

    def _spawn_rock(self, size: int, x: float | None = None, y: float | None = None) -> None:
        radius = size * 6
        if x is None:
            x = self._rng.uniform(0, self._w)
            y = self._rng.uniform(0, self._h)
            if self._w > 0:
                dx = x - self._ship_x
                dy = y - self._ship_y
                if math.sqrt(dx * dx + dy * dy) < 100:
                    x = (x + self._w / 2) % self._w
        speed = self._rng.uniform(self._ROCK_SPEED_MIN, self._ROCK_SPEED_MAX)
        angle = self._rng.uniform(0, 2 * math.pi)
        verts = []
        n_verts = self._rng.randint(6, 10)
        for i in range(n_verts):
            a = 2 * math.pi * i / n_verts
            r = radius * self._rng.uniform(0.7, 1.0)
            verts.append((math.cos(a) * r, math.sin(a) * r))
        self._rocks.append(
            {
                "x": x,
                "y": y,
                "vx": speed * math.cos(angle),
                "vy": speed * math.sin(angle),
                "radius": radius,
                "size": size,
                "verts": verts,
                "rot": self._rng.uniform(0, 2 * math.pi),
                "rot_speed": self._rng.uniform(-1.5, 1.5),
            }
        )

    def _init(self, w: int, h: int) -> None:
        self._w = w
        self._h = h
        self._init_state()

    def _wrap(self, x: float, y: float) -> tuple[float, float]:
        return x % self._w, y % self._h

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h:
            self._init(w, h)
        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        dt = min(dt, 0.05)
        self._prev_t = t
        dim = np.array(palette.dim, dtype=np.uint8)
        hi = np.array(palette.highlight, dtype=np.uint8)
        acc = np.array(palette.accent, dtype=np.uint8)
        pri = np.array(palette.primary, dtype=np.uint8)
        self._retarget_timer -= dt
        if self._retarget_timer <= 0:
            if self._rocks:
                nearest = min(
                    self._rocks,
                    key=lambda r: (r["x"] - self._ship_x) ** 2 + (r["y"] - self._ship_y) ** 2,
                )
                dx = nearest["x"] - self._ship_x
                dy = nearest["y"] - self._ship_y
                self._target_angle = math.atan2(dy, dx) + self._rng.uniform(-0.3, 0.3)
            else:
                self._target_angle = self._rng.uniform(0, 2 * math.pi)
            self._retarget_timer = self._rng.uniform(0.5, 1.5)
        angle_diff = (self._target_angle - self._ship_angle + math.pi) % (2 * math.pi) - math.pi
        self._ship_angle += angle_diff * 3.0 * dt
        thrust = 0.3 + 0.3 * math.sin(t * 2.0)
        self._ship_vx += math.cos(self._ship_angle) * self._SHIP_SPEED * thrust * dt
        self._ship_vy += math.sin(self._ship_angle) * self._SHIP_SPEED * thrust * dt
        speed = math.sqrt(self._ship_vx**2 + self._ship_vy**2)
        max_speed = self._SHIP_SPEED * 1.5
        if speed > max_speed:
            self._ship_vx *= max_speed / speed
            self._ship_vy *= max_speed / speed
        self._ship_x, self._ship_y = self._wrap(
            self._ship_x + self._ship_vx * dt,
            self._ship_y + self._ship_vy * dt,
        )
        self._fire_timer -= dt
        if self._fire_timer <= 0 and self._rocks:
            self._fire_timer = self._FIRE_INTERVAL + self._rng.uniform(-0.2, 0.2)
            self._bullets.append(
                {
                    "x": self._ship_x + math.cos(self._ship_angle) * self._SHIP_SIZE,
                    "y": self._ship_y + math.sin(self._ship_angle) * self._SHIP_SIZE,
                    "vx": math.cos(self._ship_angle) * self._BULLET_SPEED + self._ship_vx * 0.3,
                    "vy": math.sin(self._ship_angle) * self._BULLET_SPEED + self._ship_vy * 0.3,
                    "life": self._BULLET_LIFE,
                }
            )
        new_bullets = []
        for b in self._bullets:
            b["x"], b["y"] = self._wrap(b["x"] + b["vx"] * dt, b["y"] + b["vy"] * dt)
            b["life"] -= dt
            if b["life"] > 0:
                new_bullets.append(b)
        self._bullets = new_bullets
        new_rocks = []
        for rock in self._rocks:
            rock["x"], rock["y"] = self._wrap(
                rock["x"] + rock["vx"] * dt,
                rock["y"] + rock["vy"] * dt,
            )
            rock["rot"] += rock["rot_speed"] * dt
            destroyed = False
            for b in self._bullets:
                dx = b["x"] - rock["x"]
                dy = b["y"] - rock["y"]
                if dx * dx + dy * dy < rock["radius"] ** 2:
                    destroyed = True
                    b["life"] = 0
                    for _ in range(20):
                        angle = self._rng.uniform(0, 2 * math.pi)
                        spd = self._rng.uniform(20, 80)
                        self._particles.append(
                            {
                                "x": rock["x"],
                                "y": rock["y"],
                                "vx": rock["vx"] * 0.3 + math.cos(angle) * spd,
                                "vy": rock["vy"] * 0.3 + math.sin(angle) * spd,
                                "life": self._rng.uniform(0.3, 0.8),
                            }
                        )
                    if rock["size"] > 1:
                        for _ in range(2):
                            self._spawn_rock(rock["size"] - 1, rock["x"], rock["y"])
                    break
            if not destroyed:
                new_rocks.append(rock)
        self._rocks = new_rocks
        new_particles = []
        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] > 0:
                new_particles.append(p)
        self._particles = new_particles
        if len(self._rocks) < 3:
            for _ in range(self._N_ROCKS - len(self._rocks)):
                self._spawn_rock(size=3)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim
        for rock in self._rocks:
            cos_r = math.cos(rock["rot"])
            sin_r = math.sin(rock["rot"])
            pts = []
            for vx, vy in rock["verts"]:
                rx = vx * cos_r - vy * sin_r + rock["x"]
                ry = vx * sin_r + vy * cos_r + rock["y"]
                pts.append((int(rx), int(ry)))
            draw_wrapped_polygon(frame, pts, acc, w, h)
        s = self._SHIP_SIZE
        cos_a = math.cos(self._ship_angle)
        sin_a = math.sin(self._ship_angle)
        ship_pts = [
            (int(self._ship_x + cos_a * s), int(self._ship_y + sin_a * s)),
            (
                int(self._ship_x + math.cos(self._ship_angle + 2.4) * s * 0.8),
                int(self._ship_y + math.sin(self._ship_angle + 2.4) * s * 0.8),
            ),
            (
                int(self._ship_x + math.cos(self._ship_angle - 2.4) * s * 0.8),
                int(self._ship_y + math.sin(self._ship_angle - 2.4) * s * 0.8),
            ),
        ]
        draw_filled_wrapped_polygon(frame, ship_pts, pri, w, h)
        for b in self._bullets:
            bx = int(b["x"])
            by = int(b["y"])
            for ox in (-w, 0, w):
                for oy in (-h, 0, h):
                    px = bx + ox
                    py = by + oy
                    if 0 <= px < w and 0 <= py < h:
                        frame[py, px] = hi
                        if px + 1 < w:
                            frame[py, px + 1] = hi
                        if py + 1 < h:
                            frame[py + 1, px] = hi
        for p in self._particles:
            px = int(p["x"])
            py = int(p["y"])
            b = p["life"] / 0.8
            color = (acc * b + dim * (1 - b)).astype(np.uint8)
            for ox in (-w, 0, w):
                for oy in (-h, 0, h):
                    rx = px + ox
                    ry = py + oy
                    if 0 <= rx < w and 0 <= ry < h:
                        frame[ry, rx] = color
        return frame


asteroids = _AsteroidsEffect()
