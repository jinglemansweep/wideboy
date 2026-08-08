from __future__ import annotations

import logging
from typing import Any

import pygame

from ...render.palette import Palette
from ..base import Background
from ._base import Effect
from .airwolf import airwolf
from .asteroids import asteroids
from .aurora import aurora
from .boids import boids
from .breakout import breakout
from .bubbles import bubbles
from .cityscape import cityscape
from .conveyor import conveyor
from .equalizer import equalizer
from .flappy import flappy
from .gradient import gradient_scroll
from .life import life
from .lightning import lightning
from .mandelbrot import mandelbrot
from .matrix_rain import matrix_rain
from .plasma import plasma
from .rings import rings
from .scanlines import scanlines
from .slosh import slosh
from .snow import snow
from .starfield import starfield
from .tetris import tetris
from .traffic import traffic
from .waves import waves

logger = logging.getLogger(__name__)

EFFECTS = {
    plasma.name: plasma,
    gradient_scroll.name: gradient_scroll,
    starfield.name: starfield,
    waves.name: waves,
    matrix_rain.name: matrix_rain,
    aurora.name: aurora,
    equalizer.name: equalizer,
    rings.name: rings,
    snow.name: snow,
    scanlines.name: scanlines,
    bubbles.name: bubbles,
    traffic.name: traffic,
    slosh.name: slosh,
    airwolf.name: airwolf,
    lightning.name: lightning,
    life.name: life,
    mandelbrot.name: mandelbrot,
    conveyor.name: conveyor,
    breakout.name: breakout,
    boids.name: boids,
    cityscape.name: cityscape,
    tetris.name: tetris,
    asteroids.name: asteroids,
    flappy.name: flappy,
}


_EXTRA_TAGS: dict[str, set[str]] = {}


def set_extra_tags(extra: dict[str, list[str]]) -> None:
    _EXTRA_TAGS.clear()
    for name, tags in extra.items():
        if tags:
            _EXTRA_TAGS[name] = set(tags)


def get_effect_tags(name: str) -> set[str]:
    effect = EFFECTS.get(name)
    built_in = set(effect.tags) if effect else set()
    return built_in | _EXTRA_TAGS.get(name, set())


def get_effects_by_tags(tags: list[str] | None) -> dict[str, Effect]:
    if not tags:
        return dict(EFFECTS)
    tag_set = set(tags)
    return {name: effect for name, effect in EFFECTS.items() if tag_set & get_effect_tags(name)}


def get_effect_metadata() -> list[dict[str, Any]]:
    return [
        {
            "name": effect.name,
            "default_palette": effect.default_palette,
            "tags": sorted(get_effect_tags(effect.name)),
        }
        for effect in EFFECTS.values()
    ]


def get_all_tags() -> list[str]:
    tags: set[str] = set()
    for name in EFFECTS:
        tags.update(get_effect_tags(name))
    return sorted(tags)


class ProceduralBackground(Background):
    def __init__(self, settings: dict[str, Any] | None = None) -> None:
        super().__init__(settings)
        s = settings or {}
        self._effect_name = s.get("effect", "plasma")
        logger.info("Procedural effect: %s", self._effect_name)
        self._speed = float(s.get("speed", 1.0))
        self._time = 0.0
        self._resolver = s.get("_palette_resolver")

    def update(self, dt: float) -> None:
        self._time += dt * self._speed
        if self._resolver:
            self._resolver.update(dt)

    def set_effect(self, name: str) -> None:
        if name in EFFECTS:
            self._effect_name = name
            self._time = 0.0
            logger.info("Effect changed: %s", name)

    def set_speed(self, speed: float) -> None:
        self._speed = max(0.1, min(10.0, speed))

    def set_palette(self, name: str) -> None:
        if self._resolver:
            self._resolver.set_base_name(name)
            logger.info("Palette changed: %s", name)

    def get_palette(self) -> str:
        if self._resolver:
            return self._resolver.base_name
        return ""

    _SCALE_EFFECTS = {"aurora", "mandelbrot"}

    def render(self, surface: pygame.Surface) -> None:
        w, h = surface.get_size()
        fn = EFFECTS.get(self._effect_name, plasma)
        palette = self._resolver.palette if self._resolver else Palette()
        if self._effect_name in self._SCALE_EFFECTS:
            rw, rh = max(1, w // 2), max(1, h // 2)
            pixels = fn(self._time, rw, rh, palette)
            small = pygame.surfarray.make_surface(pixels.transpose(1, 0, 2))
            surf = pygame.transform.scale(small, (w, h))
        else:
            pixels = fn(self._time, w, h, palette)
            surf = pygame.surfarray.make_surface(pixels.transpose(1, 0, 2))
        surface.blit(surf, (0, 0))
