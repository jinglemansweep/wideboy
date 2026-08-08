from __future__ import annotations

from collections import deque

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import sample_palette

_GLYPH_W = 5
_GLYPH_H = 7

_GLYPH_DATA: dict[str, list[str]] = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["01110", "10001", "00001", "00110", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "#": ["00000", "10101", "11111", "10101", "11111", "10101", "00000"],
}

_GLYPHS: dict[str, np.ndarray] = {
    ch: np.array([[c == "1" for c in row] for row in rows], dtype=bool)
    for ch, rows in _GLYPH_DATA.items()
}


def _draw_text(
    frame: np.ndarray,
    text: str,
    x: int,
    y: int,
    scale: int,
    color: np.ndarray,
) -> int:
    for i, ch in enumerate(text):
        glyph = _GLYPHS.get(ch)
        if glyph is None:
            continue
        gx = x + i * (_GLYPH_W + 1) * scale
        for gy in range(_GLYPH_H):
            for gx_col in range(_GLYPH_W):
                if glyph[gy, gx_col]:
                    px = gx + gx_col * scale
                    py = y + gy * scale
                    frame[py : py + scale, px : px + scale] = color
    return x + len(text) * (_GLYPH_W + 1) * scale


def _text_width(text: str, scale: int) -> int:
    return max(0, len(text) * (_GLYPH_W + 1) * scale - scale)


class _PrimesEffect(Effect):
    name = "primes"
    default_palette = "neon"
    tags = ("geometric", "dark", "calm")

    _RATE = 14.0
    _MAX_N = 99991
    _SCROLL_SPEED = 35.0
    _BAR_W = 5
    _BAR_GAP = 2

    def __init__(self) -> None:
        self._n = 2
        self._primes: list[int] = [2]
        self._bars: deque[dict] = deque()
        self._acc = 0.0
        self._flash = 0.0
        self._prev_t = -1.0
        self._w = 0
        self._h = 0

    def _init(self) -> None:
        self._n = 2
        self._primes = [2]
        self._bars.clear()
        self._acc = 0.0
        self._flash = 0.0

    def _is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        limit = int(n**0.5) + 1
        for p in self._primes:
            if p > limit:
                break
            if n % p == 0:
                return False
        return True

    def _step_to(self, target: int, sky_right: int) -> None:
        slot = self._BAR_W + self._BAR_GAP
        while self._n <= target:
            if self._is_prime(self._n):
                gap = self._n - self._primes[-1]
                self._primes.append(self._n)
                self._flash = 1.0
                insert_x = sky_right
                if self._bars and self._bars[-1]["x"] > sky_right - slot:
                    insert_x = self._bars[-1]["x"] - slot
                self._bars.append({"x": insert_x, "gap": gap})
            self._n += 1
            if self._n > self._MAX_N:
                self._init()
                return

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._prev_t < 0 or t < self._prev_t or self._w != w or self._h != h:
            self._w, self._h = w, h
            self._init()
        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        self._prev_t = t

        sky_left = min(250, w // 3)
        sky_right = w - 8
        sky_top = 6
        sky_bottom = h - 4
        sky_h = sky_bottom - sky_top

        self._acc += dt * self._RATE
        steps = int(self._acc)
        self._acc -= steps
        if steps > 0:
            self._step_to(self._n + steps - 1, sky_right)

        self._flash = max(0.0, self._flash - dt * 3.5)

        for bar in self._bars:
            bar["x"] -= self._SCROLL_SPEED * dt
        while self._bars and self._bars[0]["x"] < sky_left - self._BAR_W:
            self._bars.popleft()

        colors = np.array(
            [palette.dim, palette.primary, palette.secondary, palette.accent, palette.highlight],
            dtype=np.float32,
        )
        dim = np.array(palette.dim, dtype=np.float32)
        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:] = dim

        div_color = dim * 0.6 + np.array(palette.secondary, dtype=np.float32) * 0.4
        frame[:, sky_left - 4 : sky_left - 3] = div_color

        for bar in self._bars:
            bx = int(bar["x"])
            gap = bar["gap"]
            gap_t = min(1.0, (gap - 2) / 18.0)
            bar_h = 2 + int(gap_t * (sky_h - 2))
            bar_color = sample_palette(colors, np.array([0.15 + gap_t * 0.85], dtype=np.float32))[0]
            by = sky_bottom - bar_h
            for px in range(bx, bx + self._BAR_W):
                if sky_left <= px < sky_right:
                    frame[by:sky_bottom, px] = bar_color
            cap_t = min(1.0, 0.3 + gap_t * 0.7)
            cap_color = sample_palette(colors, np.array([cap_t], dtype=np.float32))[0]
            if by > sky_top and sky_left <= bx < sky_right:
                frame[by - 1, bx : bx + self._BAR_W] = cap_color

        prime_str = str(self._primes[-1])
        dw = _text_width(prime_str, 3)
        dx = (sky_left - 10 - dw) // 2
        dy = (h - _GLYPH_H * 3) // 2 - 4
        pri = np.array(palette.primary, dtype=np.float32)
        hi = np.array(palette.highlight, dtype=np.float32)
        digit_color = pri * (1.0 - self._flash) + hi * self._flash
        _draw_text(frame, prime_str, dx, dy, 3, digit_color)

        idx_str = "#" + str(len(self._primes))
        iw = _text_width(idx_str, 1)
        ix = dx + (dw - iw) // 2
        iy = dy + _GLYPH_H * 3 + 4
        idx_color = dim * 0.5 + np.array(palette.accent, dtype=np.float32) * 0.5
        _draw_text(frame, idx_str, ix, iy, 1, idx_color)

        return np.clip(frame, 0, 255).astype(np.uint8)


primes = _PrimesEffect()
