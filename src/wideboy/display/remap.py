from __future__ import annotations

import pygame


def remap_logical_to_physical(frame, output_order: list[int]):
    h, w, c = frame.shape
    n_parallel = len(output_order)
    seg_w = w // n_parallel
    segs = frame.reshape(h, n_parallel, seg_w, c)
    ordered = segs[:, output_order]
    physical = ordered.transpose(1, 0, 2, 3).reshape(h * n_parallel, seg_w, c)
    return physical


def draw_test_pattern(surface: pygame.Surface, output_order: list[int]) -> None:
    import pygame.draw as draw

    w, h = surface.get_size()
    n_segments = len(output_order)
    seg_w = w // n_segments

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
    ]

    for i in range(n_segments):
        color = colors[i % len(colors)]
        x = i * seg_w
        draw.rect(surface, color, (x, 0, seg_w, h))

        font = pygame.font.SysFont(None, min(h // 2, 24))
        label = font.render(f"Seg {i} (out {output_order[i]})", True, (255, 255, 255))
        tx = x + (seg_w - label.get_width()) // 2
        ty = (h - label.get_height()) // 2
        surface.blit(label, (tx, ty))

    draw.line(surface, (255, 255, 255), (0, h // 2), (w, h // 2), 1)
