#!/usr/bin/env python
import argparse
import os
from pathlib import Path

import pygame
from PIL import Image

from wideboy.backgrounds.procedural import EFFECTS, ProceduralBackground

W, H = 768, 64
FPS = 30
DURATION = 30.0
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture procedural effect screenshots")
    parser.add_argument(
        "effect",
        nargs="?",
        default=None,
        help="effect name to capture (default: all effects)",
    )
    args = parser.parse_args()

    if args.effect is not None and args.effect not in EFFECTS:
        raise SystemExit(
            f"unknown effect '{args.effect}' (available: {', '.join(sorted(EFFECTS))})"
        )
    names = [args.effect] if args.effect is not None else sorted(EFFECTS)

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    surface = pygame.Surface((W, H))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in names:
        bg = ProceduralBackground({"effect": name, "speed": 1.0})

        dt = 1.0 / FPS
        for _ in range(int(DURATION * FPS)):
            bg.update(dt)
            bg.render(surface)
        path = OUT_DIR / f"{name}.png"
        arr = pygame.surfarray.array3d(surface).transpose(1, 0, 2)
        Image.fromarray(arr).save(path)
        print(f"Saved {path}")

    pygame.quit()


if __name__ == "__main__":
    main()
