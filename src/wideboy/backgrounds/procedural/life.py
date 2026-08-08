from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import palette_array, sample_palette

_GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
_LWSS = [(0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3)]
_BLINKER = [(0, 0), (0, 1), (0, 2)]
_TOAD = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)]
_BEACON = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (2, 3), (3, 2), (3, 3)]
_BLOCK = [(0, 0), (0, 1), (1, 0), (1, 1)]
_PENTADECATHLON = [
    (0, 2),
    (0, 8),
    (2, 0),
    (2, 1),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (2, 9),
    (2, 10),
    (4, 2),
    (4, 8),
]


class _LifeEffect(Effect):
    name = "life"
    default_palette = "neon"
    tags = ("abstract", "calm", "geometric", "retro")

    _CELL = 3
    _STEP_INTERVAL = 0.3
    _SEED_DENSITY = 0.02
    _MAX_AGE = 16.0
    _STAGNANT_LIMIT = 120
    _MIN_POP = 14
    _MAX_GENERATION = 2400

    def __init__(self) -> None:
        self._rng = np.random.RandomState(7)
        self._grid: np.ndarray | None = None
        self._age: np.ndarray | None = None
        self._gw = 0
        self._gh = 0
        self._next_step_t = self._STEP_INTERVAL
        self._generation = 0
        self._last_alive = -1
        self._stagnant = 0

    def _init(self, w: int, h: int) -> None:
        self._gw = w // self._CELL
        self._gh = h // self._CELL
        self._reseed()

    def _stamp(self, grid: np.ndarray, pattern: list[tuple[int, int]]) -> None:
        gh, gw = grid.shape
        br = self._rng.randint(0, gh)
        bc = self._rng.randint(0, gw)
        fh = -1 if self._rng.random() < 0.5 else 1
        fv = -1 if self._rng.random() < 0.5 else 1
        for dr, dc in pattern:
            grid[(br + fv * dr) % gh, (bc + fh * dc) % gw] = True

    def _reseed(self) -> None:
        gw, gh = self._gw, self._gh
        grid = self._rng.random((gh, gw)) < self._SEED_DENSITY
        for _ in range(12):
            self._stamp(grid, _GLIDER)
        for _ in range(4):
            self._stamp(grid, _LWSS)
        for _ in range(8):
            self._stamp(grid, _BLINKER)
        for _ in range(6):
            self._stamp(grid, _BLOCK)
        for _ in range(3):
            self._stamp(grid, _BEACON)
        for _ in range(3):
            self._stamp(grid, _TOAD)
        self._stamp(grid, _PENTADECATHLON)
        self._grid = grid
        self._age = np.where(grid, 0.0, -1.0).astype(np.float32)
        self._generation = 0
        self._stagnant = 0
        self._last_alive = -1

    def _step(self) -> None:
        g = self._grid.astype(np.uint8)
        neighbors = (
            np.roll(g, 1, 0)
            + np.roll(g, -1, 0)
            + np.roll(g, 1, 1)
            + np.roll(g, -1, 1)
            + np.roll(np.roll(g, 1, 0), 1, 1)
            + np.roll(np.roll(g, 1, 0), -1, 1)
            + np.roll(np.roll(g, -1, 0), 1, 1)
            + np.roll(np.roll(g, -1, 0), -1, 1)
        )
        alive = self._grid
        survives = alive & ((neighbors == 2) | (neighbors == 3))
        born = (~alive) & (neighbors == 3)
        new_grid = survives | born

        age = self._age
        age = np.where(survives, age + 1.0, np.where(born, 0.0, -1.0))

        self._grid = new_grid
        self._age = age
        self._generation += 1

        alive_count = int(new_grid.sum())
        if alive_count == self._last_alive:
            self._stagnant += 1
        else:
            self._stagnant = 0
        self._last_alive = alive_count

        if (
            alive_count < self._MIN_POP
            or self._stagnant >= self._STAGNANT_LIMIT
            or self._generation >= self._MAX_GENERATION
        ):
            self._reseed()

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._grid is None or self._gw != w // self._CELL or self._gh != h // self._CELL:
            self._init(w, h)

        while t >= self._next_step_t:
            self._step()
            self._next_step_t += self._STEP_INTERVAL

        cell = self._CELL
        gh, gw = self._gh, self._gw

        colors = palette_array(palette)
        ramp = np.array(
            [colors[0], colors[2], colors[1], colors[3]],
            dtype=np.float32,
        )
        gx = np.linspace(0.0, 1.0, gw, dtype=np.float32)
        gy = np.linspace(0.0, 1.0, gh, dtype=np.float32)[:, None]
        pos = (gx + gy) * 0.5
        base = sample_palette(ramp, pos)

        age = self._age
        vitality = np.clip(1.0 - age / self._MAX_AGE, 0.55, 1.0)[..., None]
        birth = np.clip(1.0 - age / 2.5, 0.0, 1.0)[..., None]
        highlight = colors[3]
        alive_rgb = base * vitality + highlight * birth * 0.18

        bg = (colors[4] * 0.12)[None, None, :]
        cell_rgb = np.where(self._grid[..., None], alive_rgb, bg)

        big = np.kron(cell_rgb, np.ones((cell, cell, 1), dtype=np.float32))
        frame = np.full((h, w, 3), colors[4] * 0.15, dtype=np.float32)
        frame[: gh * cell, : gw * cell] = big
        return np.clip(frame, 0, 255).astype(np.uint8)


life = _LifeEffect()
