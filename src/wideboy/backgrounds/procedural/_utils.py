from __future__ import annotations

import numpy as np

from ...render.palette import Palette


def palette_array(p: Palette) -> np.ndarray:
    return np.array(
        [p.primary, p.secondary, p.accent, p.highlight, p.dim],
        dtype=np.float32,
    )


def sample_palette(colors: np.ndarray, t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0.0, 1.0)
    idx = t * (len(colors) - 1)
    lo = np.floor(idx).astype(np.int32)
    hi = np.minimum(lo + 1, len(colors) - 1)
    frac = (idx - lo)[..., np.newaxis]
    return colors[lo] * (1 - frac) + colors[hi] * frac


def draw_line(frame: np.ndarray, x0: int, y0: int, x1: int, y1: int,
              color: np.ndarray, w: int, h: int) -> None:
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    if dx > w or dy > h:
        return
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < w and 0 <= y0 < h:
            frame[y0, x0] = color
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def draw_wrapped_polygon(frame: np.ndarray, pts: list[tuple[int, int]],
                         color: np.ndarray, w: int, h: int) -> None:
    for ox in (-w, 0, w):
        for oy in (-h, 0, h):
            offset_pts = [(x + ox, y + oy) for x, y in pts]
            all_outside = all(
                x < 0 or x >= w or y < 0 or y >= h for x, y in offset_pts
            )
            if all_outside:
                continue
            for i in range(len(offset_pts)):
                p1 = offset_pts[i]
                p2 = offset_pts[(i + 1) % len(offset_pts)]
                draw_line(frame, p1[0], p1[1], p2[0], p2[1], color, w, h)


def draw_filled_wrapped_polygon(frame: np.ndarray, pts: list[tuple[int, int]],
                                color: np.ndarray, w: int, h: int) -> None:
    for ox in (-w, 0, w):
        for oy in (-h, 0, h):
            offset_pts = [(x + ox, y + oy) for x, y in pts]
            all_outside = all(
                x < -20 or x >= w + 20 or y < -20 or y >= h + 20 for x, y in offset_pts
            )
            if all_outside:
                continue
            ys = [p[1] for p in offset_pts]
            min_y = max(0, min(ys))
            max_y = min(h - 1, max(ys))
            for y in range(min_y, max_y + 1):
                intersections = []
                n = len(offset_pts)
                for i in range(n):
                    x1, y1 = offset_pts[i]
                    x2, y2 = offset_pts[(i + 1) % n]
                    if (y1 <= y < y2) or (y2 <= y < y1):
                        if y2 != y1:
                            x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                            intersections.append(int(x))
                intersections.sort()
                for i in range(0, len(intersections) - 1, 2):
                    x_start = max(0, intersections[i])
                    x_end = min(w - 1, intersections[i + 1])
                    if x_start <= x_end:
                        frame[y, x_start:x_end + 1] = color


def draw_obj(frame: np.ndarray, obj: np.ndarray, x: int, y: int,
             colors: list, max_y: int) -> None:
    oh, ow = obj.shape
    h, w = frame.shape[:2]
    for oy in range(oh):
        for ox in range(ow):
            ci = obj[oy, ox]
            if ci == 0:
                continue
            py = y + oy
            px = x + ox
            if 0 <= py < max_y and 0 <= px < w:
                frame[py, px] = colors[ci % len(colors)]
