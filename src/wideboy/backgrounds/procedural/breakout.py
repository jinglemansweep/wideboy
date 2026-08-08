from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _BreakoutEffect(Effect):
    name = "breakout"
    default_palette = "neon"
    tags = ("game", "retro", "energetic")

    _ROWS = 5
    _BRICK_H = 4
    _BRICK_GAP = 1
    _PADDLE_W = 30
    _PADDLE_H = 3
    _BALL_SIZE = 3
    _BALL_SPEED = 150.0
    _PADDLE_SPEED = 400.0
    _MIN_BOUNCE_ANGLE = math.pi / 7

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._prev_t = -1.0
        self._bricks: np.ndarray | None = None
        self._brick_cols = 0
        self._brick_w = 0
        self._brick_offset_x = 0
        self._ball_x = 0.0
        self._ball_y = 0.0
        self._ball_vx = 0.0
        self._ball_vy = 0.0
        self._paddle_x = 0.0
        self._paddle_aim_offset = 0.0
        self._last_vy_sign = 0.0
        self._rng = np.random.RandomState(42)
        self._reset()

    def _launch_ball(self) -> None:
        self._ball_x = self._paddle_x
        self._ball_y = self._h - 12
        angle = self._rng.uniform(-math.pi / 4, math.pi / 4)
        self._ball_vx = self._BALL_SPEED * math.sin(angle)
        self._ball_vy = -self._BALL_SPEED * math.cos(angle)
        self._paddle_aim_offset = 0.0

    def _reset(self) -> None:
        if self._bricks is not None:
            self._bricks[:] = True
        if self._w > 0:
            self._paddle_x = self._w / 2
            self._launch_ball()

    def _init(self, w: int, h: int) -> None:
        self._w = w
        self._h = h
        self._brick_w = max(4, w // 48)
        self._brick_cols = w // (self._brick_w + self._BRICK_GAP)
        total_w = self._brick_cols * (self._brick_w + self._BRICK_GAP) - self._BRICK_GAP
        self._brick_offset_x = (w - total_w) // 2
        self._bricks = np.ones((self._ROWS, self._brick_cols), dtype=bool)
        self._paddle_x = w / 2
        self._launch_ball()

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h or self._bricks is None:
            self._init(w, h)

        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        dt = min(dt, 0.05)
        self._prev_t = t

        dim = np.array(palette.dim, dtype=np.uint8)
        pri = np.array(palette.primary, dtype=np.uint8)
        sec = np.array(palette.secondary, dtype=np.uint8)
        acc = np.array(palette.accent, dtype=np.uint8)
        hi = np.array(palette.highlight, dtype=np.uint8)
        row_colors = [hi, acc, pri, sec, pri]

        paddle_y = h - 8

        vy_sign = 1.0 if self._ball_vy > 0 else -1.0
        if vy_sign != self._last_vy_sign:
            self._last_vy_sign = vy_sign
            if vy_sign > 0:
                self._paddle_aim_offset = self._rng.uniform(
                    -self._PADDLE_W * 0.35, self._PADDLE_W * 0.35
                )
        wobble = math.sin(t * 2.1 + 0.5) * 20 + math.sin(t * 3.7 + 1.8) * 12

        if self._ball_vy > 0 and self._ball_vy != 0:
            time_to_paddle = max(0.0, (paddle_y - self._ball_y) / self._ball_vy)
            predicted_x = self._ball_x + self._ball_vx * time_to_paddle
            for _ in range(10):
                if predicted_x < 0:
                    predicted_x = -predicted_x
                elif predicted_x > w:
                    predicted_x = 2 * w - predicted_x
                else:
                    break
            target_x = predicted_x + self._paddle_aim_offset
        else:
            target_x = self._ball_x + wobble

        target_x = np.clip(target_x, self._PADDLE_W / 2, w - self._PADDLE_W / 2)
        diff = target_x - self._paddle_x
        max_move = self._PADDLE_SPEED * dt
        if abs(diff) > max_move:
            self._paddle_x += max_move * (1.0 if diff > 0 else -1.0)
        else:
            self._paddle_x = target_x
        self._paddle_x = np.clip(self._paddle_x, self._PADDLE_W / 2, w - self._PADDLE_W / 2)

        steps = max(1, int(self._BALL_SPEED * dt / 2))
        sub_dt = dt / steps

        for _ in range(steps):
            self._ball_x += self._ball_vx * sub_dt
            self._ball_y += self._ball_vy * sub_dt

            if self._ball_x <= self._BALL_SIZE / 2:
                self._ball_x = self._BALL_SIZE / 2
                self._ball_vx = abs(self._ball_vx)
            elif self._ball_x >= w - self._BALL_SIZE / 2:
                self._ball_x = w - self._BALL_SIZE / 2
                self._ball_vx = -abs(self._ball_vx)

            if self._ball_y <= self._BALL_SIZE / 2:
                self._ball_y = self._BALL_SIZE / 2
                self._ball_vy = abs(self._ball_vy)

            px0 = self._paddle_x - self._PADDLE_W / 2
            px1 = self._paddle_x + self._PADDLE_W / 2
            py0 = paddle_y
            py1 = paddle_y + self._PADDLE_H
            bx = self._ball_x
            by = self._ball_y
            br = self._BALL_SIZE / 2
            if (
                self._ball_vy > 0
                and bx + br > px0
                and bx - br < px1
                and by + br > py0
                and by - br < py1
            ):
                hit_pos = np.clip((bx - self._paddle_x) / (self._PADDLE_W / 2), -1.0, 1.0)
                angle = hit_pos * (math.pi / 3)
                if abs(angle) < self._MIN_BOUNCE_ANGLE:
                    angle = self._MIN_BOUNCE_ANGLE * (1 if angle >= 0 else -1)
                self._ball_vx = self._BALL_SPEED * math.sin(angle)
                self._ball_vy = -self._BALL_SPEED * math.cos(angle)
                self._ball_y = py0 - br

            for row in range(self._ROWS):
                for col in range(self._brick_cols):
                    if not self._bricks[row, col]:
                        continue
                    brick_x = self._brick_offset_x + col * (self._brick_w + self._BRICK_GAP)
                    brick_y = row * (self._BRICK_H + self._BRICK_GAP)
                    if (
                        bx + br > brick_x
                        and bx - br < brick_x + self._brick_w
                        and by + br > brick_y
                        and by - br < brick_y + self._BRICK_H
                    ):
                        self._bricks[row, col] = False
                        overlap_left = (bx + br) - brick_x
                        overlap_right = (brick_x + self._brick_w) - (bx - br)
                        overlap_top = (by + br) - brick_y
                        overlap_bottom = (brick_y + self._BRICK_H) - (by - br)
                        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                        if min_overlap == overlap_left or min_overlap == overlap_right:
                            self._ball_vx = -self._ball_vx
                        else:
                            self._ball_vy = -self._ball_vy
                        break
                else:
                    continue
                break

            if self._ball_y > h + 10:
                self._reset()

        if not self._bricks.any():
            self._reset()

        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim

        for row in range(self._ROWS):
            for col in range(self._brick_cols):
                if not self._bricks[row, col]:
                    continue
                bx0 = self._brick_offset_x + col * (self._brick_w + self._BRICK_GAP)
                by0 = row * (self._BRICK_H + self._BRICK_GAP)
                bx1 = min(bx0 + self._brick_w, w)
                by1 = min(by0 + self._BRICK_H, h)
                frame[by0:by1, bx0:bx1] = row_colors[row]

        px0 = max(0, int(self._paddle_x - self._PADDLE_W / 2))
        px1 = min(w, int(self._paddle_x + self._PADDLE_W / 2))
        py0 = max(0, paddle_y)
        py1 = min(h, paddle_y + self._PADDLE_H)
        frame[py0:py1, px0:px1] = hi

        bx0 = max(0, int(self._ball_x - self._BALL_SIZE / 2))
        by0 = max(0, int(self._ball_y - self._BALL_SIZE / 2))
        bx1 = min(w, int(self._ball_x + self._BALL_SIZE / 2) + 1)
        by1 = min(h, int(self._ball_y + self._BALL_SIZE / 2) + 1)
        frame[by0:by1, bx0:bx1] = hi

        return frame


breakout = _BreakoutEffect()
