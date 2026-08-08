from __future__ import annotations

import numpy as np

from ...render.palette import Palette


class Effect:
    name: str = ""
    default_palette: str = "neon"
    tags: tuple[str, ...] = ()

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        raise NotImplementedError
