from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _TetrisEffect(Effect):
    name = "tetris"
    default_palette = "neon"
    tags = ("game", "retro")

    _BLOCK = 8
    _COLS = 96
    _ROWS = 8
    _DROP_SPEED = 200.0

    _PIECES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[0, 1, 0], [1, 1, 1]],
        [[0, 1, 1], [1, 1, 0]],
        [[1, 1, 0], [0, 1, 1]],
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0, 0], [1, 1, 1]],
    ]

    _COLORS = [
        (0, 255, 255),
        (255, 255, 0),
        (160, 0, 255),
        (0, 255, 0),
        (255, 0, 0),
        (255, 160, 0),
        (0, 80, 255),
    ]

    _AI_AGG_HEIGHT = -0.51
    _AI_LINES = 0.76
    _AI_HOLES = -0.36
    _AI_BUMPINESS = -0.18

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._prev_t = -1.0
        self._board: np.ndarray | None = None
        self._rng = np.random.RandomState(42)
        self._cur_piece = 0
        self._cur_rot = 0
        self._cur_col = 0
        self._cur_row = 0
        self._target_row = 0
        self._drop_y = 0.0
        self._flash_rows: list[int] = []
        self._flash_t = 0.0
        self._next_piece()

    def _find_drop_row(self, shape: list[list[int]], col: int) -> int:
        piece_rows = len(shape)
        for r in range(self._ROWS - 1, piece_rows - 1, -1):
            can_place = True
            for pr in range(piece_rows):
                for pc in range(len(shape[0])):
                    if shape[pr][pc] and self._board[r - piece_rows + 1 + pr, col + pc] >= 0:
                        can_place = False
                        break
                if not can_place:
                    break
            if can_place:
                return r - piece_rows + 1
        return -1

    def _next_piece(self) -> None:
        self._cur_piece = self._rng.randint(0, len(self._PIECES))
        best_score = -1e9
        best_rot = 0
        best_col = self._COLS // 2
        for rot in range(4):
            shape = self._rotate(self._PIECES[self._cur_piece], rot)
            max_col = self._COLS - len(shape[0]) + 1
            for col in range(0, max_col, 8):
                score = self._evaluate_placement(shape, col)
                if score > best_score:
                    best_score = score
                    best_rot = rot
                    best_col = col
        shape = self._rotate(self._PIECES[self._cur_piece], best_rot)
        max_col = self._COLS - len(shape[0]) + 1
        for col in range(max(0, best_col - 7), min(max_col, best_col + 8)):
            score = self._evaluate_placement(shape, col)
            if score > best_score:
                best_score = score
                best_col = col
        self._cur_rot = best_rot
        self._cur_col = best_col
        shape = self._rotate(self._PIECES[self._cur_piece], best_rot)
        self._cur_row = -len(shape)
        self._drop_y = float(self._cur_row * self._BLOCK)
        if self._board is not None:
            self._target_row = self._find_drop_row(shape, best_col)
        else:
            self._target_row = self._ROWS - len(shape)

    def _evaluate_placement(self, shape: list[list[int]], col: int) -> float:
        board = self._board
        if board is None:
            return 0.0
        piece_rows = len(shape)
        piece_cols = len(shape[0])
        drop_row = self._find_drop_row(shape, col)
        if drop_row < 0:
            return -1e8
        test_board = board.copy()
        for pr in range(piece_rows):
            for pc in range(piece_cols):
                if shape[pr][pc]:
                    test_board[drop_row + pr, col + pc] = 1
        occupied = test_board >= 0
        col_has_block = occupied.any(axis=0)
        col_top = np.where(col_has_block, np.argmax(occupied, axis=0), self._ROWS).astype(np.int32)
        col_heights = self._ROWS - col_top
        agg_height = float(col_heights.sum())
        filled = np.cumsum(occupied, axis=0)
        total_below = np.where(
            col_has_block,
            filled[-1, :] - np.choose(col_top, filled, mode="clip"),
            0,
        )
        holes = int(total_below.sum())
        bumpiness = float(np.abs(np.diff(col_heights)).sum())
        lines = int(np.all(occupied, axis=1).sum())
        return (
            self._AI_AGG_HEIGHT * agg_height
            + self._AI_LINES * lines
            + self._AI_HOLES * holes
            + self._AI_BUMPINESS * bumpiness
        )

    def _rotate(self, shape: list[list[int]], times: int) -> list[list[int]]:
        s = shape
        for _ in range(times):
            s = [list(row) for row in zip(*s[::-1])]
        return s

    def _lock_piece(self) -> None:
        shape = self._rotate(self._PIECES[self._cur_piece], self._cur_rot)
        piece_rows = len(shape)
        piece_cols = len(shape[0])
        drop_row = self._target_row
        if drop_row < 0:
            self._reset()
            return
        for pr in range(piece_rows):
            for pc in range(piece_cols):
                if shape[pr][pc]:
                    self._board[drop_row + pr, self._cur_col + pc] = self._cur_piece
        cleared = []
        for r in range(self._ROWS):
            if np.all(self._board[r, :] >= 0):
                cleared.append(r)
        if cleared:
            self._flash_rows = cleared
            self._flash_t = 0.0
        self._next_piece()

    def _reset(self) -> None:
        if self._board is not None:
            self._board[:] = -1
        self._flash_rows = []
        self._next_piece()

    def _init(self, w: int, h: int) -> None:
        self._w = w
        self._h = h
        self._board = np.full((self._ROWS, self._COLS), -1, dtype=np.int8)
        self._next_piece()

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h or self._board is None:
            self._init(w, h)
        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        dt = min(dt, 0.05)
        self._prev_t = t
        dim = np.array(palette.dim, dtype=np.uint8)
        if self._flash_rows:
            self._flash_t += dt
            if self._flash_t > 0.15:
                for r in sorted(self._flash_rows, reverse=True):
                    self._board = np.delete(self._board, r, axis=0)
                    self._board = np.insert(self._board, 0, -1, axis=0)
                self._flash_rows = []
        self._drop_y += self._DROP_SPEED * dt
        shape = self._rotate(self._PIECES[self._cur_piece], self._cur_rot)
        target_y = self._target_row * self._BLOCK
        if self._drop_y >= target_y:
            self._drop_y = float(target_y)
            self._lock_piece()
            shape = self._rotate(self._PIECES[self._cur_piece], self._cur_rot)
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = dim
        for r in range(self._ROWS):
            for c in range(self._COLS):
                ci = self._board[r, c]
                if ci >= 0:
                    x0 = c * self._BLOCK
                    y0 = r * self._BLOCK
                    x1 = min(x0 + self._BLOCK, w)
                    y1 = min(y0 + self._BLOCK, h)
                    if r in self._flash_rows:
                        flash_b = 1.0 if int(self._flash_t * 20) % 2 else 0.3
                        white = np.array([255, 255, 255])
                        color = (dim * (1 - flash_b) + white * flash_b).astype(np.uint8)
                        frame[y0:y1, x0:x1] = color
                    else:
                        frame[y0:y1, x0:x1] = self._COLORS[ci]
        cur_y = int(self._drop_y)
        piece_rows = len(shape)
        piece_cols = len(shape[0])
        for pr in range(piece_rows):
            for pc in range(piece_cols):
                if shape[pr][pc]:
                    x0 = (self._cur_col + pc) * self._BLOCK
                    y0 = cur_y + pr * self._BLOCK
                    x1 = min(x0 + self._BLOCK, w)
                    y1 = min(y0 + self._BLOCK, h)
                    if x0 >= 0 and y0 >= 0:
                        frame[y0:y1, x0:x1] = self._COLORS[self._cur_piece]
        for c in range(self._COLS + 1):
            x = c * self._BLOCK
            if 0 <= x < w:
                frame[0:h, x] = (dim * 0.3).astype(np.uint8)
        for r in range(self._ROWS + 1):
            y = r * self._BLOCK
            if 0 <= y < h:
                frame[y, 0:w] = (dim * 0.3).astype(np.uint8)
        return frame


tetris = _TetrisEffect()
