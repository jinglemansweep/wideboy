from __future__ import annotations

import numpy as np

from ...render.palette import Palette
from ._base import Effect


class _CityScapeEffect(Effect):
    name = "cityscape"
    default_palette = "neon"
    tags = ("nostalgic", "calm")

    _LAYERS = (
        {
            "speed": 35.0,
            "h_min": 20,
            "h_max": 46,
            "w_min": 10,
            "w_max": 26,
            "gap": 20,
            "bright": 0.50,
            "win_prob": 0.04,
            "seed": 37,
        },
        {
            "speed": 60.0,
            "h_min": 32,
            "h_max": 58,
            "w_min": 14,
            "w_max": 32,
            "gap": 50,
            "bright": 0.85,
            "win_prob": 0.06,
            "seed": 53,
        },
    )

    _NEON = np.array(
        [
            [0, 255, 255],
            [255, 0, 255],
            [0, 255, 0],
            [255, 20, 147],
            [0, 120, 255],
            [255, 100, 0],
            [255, 255, 0],
            [148, 0, 211],
        ],
        dtype=np.float32,
    )

    def __init__(self) -> None:
        self._w = 0
        self._h = 0
        self._strips: list[tuple] = []

    def _gen_strip(
        self,
        layer: dict,
        w: int,
        h: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        rng = np.random.RandomState(layer["seed"])
        strip_w = w * 2
        body = np.zeros((h, strip_w), dtype=np.uint8)
        outline = np.zeros((h, strip_w), dtype=np.uint8)
        outline_rgb = np.zeros((h, strip_w, 3), dtype=np.float32)
        windows = np.zeros((h, strip_w), dtype=np.uint8)
        x = 0
        while x < strip_w:
            bw = rng.randint(layer["w_min"], layer["w_max"] + 1)
            bh = rng.randint(layer["h_min"], layer["h_max"] + 1)
            bh = min(bh, h - 2)
            top = h - bh
            if x + bw <= strip_w and bw >= 3:
                color = self._NEON[rng.randint(0, len(self._NEON))]
                body[top:, x : x + bw] = 1
                outline[top, x : x + bw] = 1
                outline_rgb[top, x : x + bw] = color
                outline[top:h, x] = 1
                outline_rgb[top:h, x] = color
                outline[top:h, x + bw - 1] = 1
                outline_rgb[top:h, x + bw - 1] = color
                win_prob = layer["win_prob"]
                wy = top + 4
                while wy < h - 3:
                    wx = x + 2
                    while wx < x + bw - 2:
                        if rng.random() < win_prob * 6:
                            ww = min(2, x + bw - 1 - wx)
                            wh = min(2, h - 1 - wy)
                            if ww > 0 and wh > 0:
                                windows[wy : wy + wh, wx : wx + ww] = 1
                        wx += rng.randint(4, 7)
                    wy += rng.randint(4, 7)
            x += bw + layer["gap"] + rng.randint(0, 3)
        return body, outline, outline_rgb, windows

    def _init(self, w: int, h: int) -> None:
        self._w, self._h = w, h
        self._strips = []
        for layer in self._LAYERS:
            self._strips.append(self._gen_strip(layer, w, h))

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._w != w or self._h != h:
            self._init(w, h)

        dim = np.array(palette.dim, dtype=np.float32)
        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:, :] = dim

        pal_colors = [
            np.array(palette.primary, dtype=np.float32),
            np.array(palette.secondary, dtype=np.float32),
            np.array(palette.accent, dtype=np.float32),
            np.array(palette.highlight, dtype=np.float32),
        ]

        for li, layer in enumerate(self._LAYERS):
            body_m, outline_m, outline_rgb_m, win_m = self._strips[li]
            strip_w = body_m.shape[1]
            offset = int(t * layer["speed"]) % strip_w

            if offset + w <= strip_w:
                vb = body_m[:, offset : offset + w]
                vo = outline_m[:, offset : offset + w]
                voc = outline_rgb_m[:, offset : offset + w]
                vw = win_m[:, offset : offset + w]
            else:
                r = offset + w - strip_w
                vb = np.concatenate(
                    [body_m[:, offset:], body_m[:, :r]],
                    axis=1,
                )
                vo = np.concatenate(
                    [outline_m[:, offset:], outline_m[:, :r]],
                    axis=1,
                )
                voc = np.concatenate(
                    [outline_rgb_m[:, offset:], outline_rgb_m[:, :r]],
                    axis=1,
                )
                vw = np.concatenate(
                    [win_m[:, offset:], win_m[:, :r]],
                    axis=1,
                )

            b = layer["bright"]
            fill_color = dim * (0.15 + 0.1 * b)
            body_f = vb[:, :, np.newaxis].astype(np.float32)
            frame = frame * (1 - body_f) + fill_color * body_f

            ol_f = vo[:, :, np.newaxis].astype(np.float32)
            frame = frame * (1 - ol_f) + voc * ol_f

            win_color = pal_colors[3] * 0.9 + dim * 0.1
            win_f = vw[:, :, np.newaxis].astype(np.float32)
            flicker = 0.7 + 0.3 * np.sin(t * 2.0 + li * 1.5)
            frame = frame * (1 - win_f * flicker) + win_color * win_f * flicker

        return np.clip(frame, 0, 255).astype(np.uint8)


cityscape = _CityScapeEffect()
