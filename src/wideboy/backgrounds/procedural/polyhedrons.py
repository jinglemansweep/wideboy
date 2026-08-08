from __future__ import annotations

import math

import numpy as np

from ...render.palette import Palette
from ._base import Effect
from ._utils import draw_line, sample_palette

_PHI = (1.0 + math.sqrt(5.0)) / 2.0


def _rot_x(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)


def _rot_y(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)


def _rot_z(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)


def _normalize(verts: np.ndarray) -> np.ndarray:
    return verts / np.linalg.norm(verts, axis=1, keepdims=True)


def _edges_by_min_distance(verts: np.ndarray, tol: float = 0.02) -> np.ndarray:
    d = np.linalg.norm(verts[:, None, :] - verts[None, :, :], axis=2)
    edge_len = d[d > 1e-6].min()
    n = len(verts)
    pairs = [
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if abs(d[i, j] - edge_len) <= tol * edge_len
    ]
    return np.array(pairs, dtype=np.int32)


def _tetra() -> tuple[np.ndarray, np.ndarray]:
    v = _normalize(np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=np.float32))
    return v, _edges_by_min_distance(v)


def _cube() -> tuple[np.ndarray, np.ndarray]:
    v = _normalize(
        np.array(
            [[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)],
            dtype=np.float32,
        )
    )
    return v, _edges_by_min_distance(v)


def _octa() -> tuple[np.ndarray, np.ndarray]:
    v = _normalize(
        np.array(
            [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]],
            dtype=np.float32,
        )
    )
    return v, _edges_by_min_distance(v)


def _icosa() -> tuple[np.ndarray, np.ndarray]:
    v = _normalize(
        np.array(
            [
                [0, 1, _PHI],
                [0, 1, -_PHI],
                [0, -1, _PHI],
                [0, -1, -_PHI],
                [1, _PHI, 0],
                [1, -_PHI, 0],
                [-1, _PHI, 0],
                [-1, -_PHI, 0],
                [_PHI, 0, 1],
                [_PHI, 0, -1],
                [-_PHI, 0, 1],
                [-_PHI, 0, -1],
            ],
            dtype=np.float32,
        )
    )
    return v, _edges_by_min_distance(v)


def _dodeca() -> tuple[np.ndarray, np.ndarray]:
    inv_phi = 1.0 / _PHI
    v = _normalize(
        np.array(
            [[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
            + [[0, s * inv_phi, t * _PHI] for s in (-1, 1) for t in (-1, 1)]
            + [[s * inv_phi, t * _PHI, 0] for s in (-1, 1) for t in (-1, 1)]
            + [[s * _PHI, 0, t * inv_phi] for s in (-1, 1) for t in (-1, 1)],
            dtype=np.float32,
        )
    )
    return v, _edges_by_min_distance(v)


def _prism(n: int) -> tuple[np.ndarray, np.ndarray]:
    ang = np.linspace(0, math.tau, n, endpoint=False, dtype=np.float32)
    top = np.stack([np.cos(ang), np.sin(ang), np.ones(n)], axis=1)
    bot = np.stack([np.cos(ang), np.sin(ang), -np.ones(n)], axis=1)
    v = _normalize(np.vstack([top, bot]))
    edges = []
    for k in range(n):
        edges.append((k, (k + 1) % n))
        edges.append((k + n, (k + 1) % n + n))
        edges.append((k, k + n))
    return v, np.array(edges, dtype=np.int32)


def _random_convex(rng: np.random.RandomState) -> tuple[np.ndarray, np.ndarray]:
    n = int(rng.randint(6, 10))
    pts = rng.randn(n, 3).astype(np.float32)
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    edges: set[tuple[int, int]] = set()
    for i in range(n):
        nearest = np.argsort(d[i])[1:4]
        for j in nearest:
            edges.add((min(i, int(j)), max(i, int(j))))
    return pts, np.array(sorted(edges), dtype=np.int32)


_SHAPE_BUILDERS = (
    lambda r: _tetra(),
    lambda r: _cube(),
    lambda r: _octa(),
    lambda r: _icosa(),
    lambda r: _dodeca(),
    lambda r: _prism(3),
    lambda r: _prism(4),
    lambda r: _prism(6),
    lambda r: _random_convex(r),
)


class _PolyhedronsEffect(Effect):
    name = "polyhedrons"
    default_palette = "neon"
    tags = ("geometric", "particle", "dark")

    _N_SHAPES = 5

    def __init__(self) -> None:
        self._rng = np.random.RandomState(11)
        self._shapes: list[dict] | None = None
        self._prev_t = -1.0
        self._w = 0
        self._h = 0

    def _init(self, w: int, h: int) -> None:
        self._w, self._h = w, h
        self._shapes = [self._spawn() for _ in range(self._N_SHAPES)]

    def _spawn(self) -> dict:
        builder = _SHAPE_BUILDERS[self._rng.randint(len(_SHAPE_BUILDERS))]
        verts, edges = builder(self._rng)
        return {
            "verts": verts.astype(np.float32),
            "edges": edges,
            "x": float(self._rng.uniform(0, self._w)),
            "y": float(self._rng.uniform(self._h * 0.3, self._h * 0.7)),
            "vx": float(self._rng.uniform(-25.0, 25.0)),
            "rx": float(self._rng.uniform(0, math.tau)),
            "ry": float(self._rng.uniform(0, math.tau)),
            "rz": float(self._rng.uniform(0, math.tau)),
            "vrx": float(self._rng.uniform(-0.8, 0.8)),
            "vry": float(self._rng.uniform(-0.8, 0.8)),
            "vrz": float(self._rng.uniform(-0.4, 0.4)),
            "scale": float(self._rng.uniform(self._h * 0.18, self._h * 0.32)),
            "age": float(self._rng.uniform(0.0, 8.0)),
            "lifetime": float(self._rng.uniform(10.0, 16.0)),
            "phase": float(self._rng.uniform(0.0, 1.0)),
        }

    def __call__(self, t: float, w: int, h: int, palette: Palette) -> np.ndarray:
        if self._shapes is None or self._w != w or self._h != h:
            self._init(w, h)
        dt = max(0.0, t - self._prev_t) if self._prev_t >= 0 else 1.0 / 60.0
        self._prev_t = t

        for idx in range(self._N_SHAPES):
            s = self._shapes[idx]
            s["age"] += dt
            if s["age"] > s["lifetime"]:
                self._shapes[idx] = self._spawn()
                s = self._shapes[idx]
            s["x"] += s["vx"] * dt
            s["rx"] += s["vrx"] * dt
            s["ry"] += s["vry"] * dt
            s["rz"] += s["vrz"] * dt
            margin = s["scale"] + 4.0
            if s["x"] < -margin:
                s["x"] = w + margin
            elif s["x"] > w + margin:
                s["x"] = -margin

        dim = np.array(palette.dim, dtype=np.float32)
        gradient = np.array(
            [palette.dim, palette.primary, palette.secondary, palette.accent, palette.highlight],
            dtype=np.float32,
        )
        frame = np.zeros((h, w, 3), dtype=np.float32)
        frame[:] = dim

        focal = float(h) * 4.0
        cam_z = focal

        for s in self._shapes:
            age = s["age"]
            life = s["lifetime"]
            fade_in = min(1.0, age / (life * 0.15))
            fade_out = min(1.0, (life - age) / (life * 0.15))
            alpha = max(0.0, min(fade_in, fade_out))

            rot = _rot_z(s["rz"]) @ _rot_y(s["ry"]) @ _rot_x(s["rx"])
            rotated = (rot @ s["verts"].T).T
            scaled = rotated * s["scale"]
            z_view = cam_z + scaled[:, 2]
            persp = focal / z_view
            sx = s["x"] + scaled[:, 0] * persp
            sy = s["y"] + scaled[:, 1] * persp

            zmin = float(z_view.min())
            zrange = float(z_view.max()) - zmin + 1e-6

            for ei, ej in s["edges"]:
                zmid = (z_view[ei] + z_view[ej]) * 0.5
                depth_t = 1.0 - (zmid - zmin) / zrange
                color_t = max(0.0, min(1.0, depth_t * 0.6 + s["phase"] * 0.4))
                base = sample_palette(gradient, np.array([color_t], dtype=np.float32))[0]
                color = base * alpha + dim * (1.0 - alpha)
                draw_line(
                    frame,
                    int(sx[ei]),
                    int(sy[ei]),
                    int(sx[ej]),
                    int(sy[ej]),
                    color,
                    w,
                    h,
                )

        return np.clip(frame, 0, 255).astype(np.uint8)


polyhedrons = _PolyhedronsEffect()
