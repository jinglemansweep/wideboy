from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pygame

from .base import Background

logger = logging.getLogger(__name__)


class CompositeBackground(Background):
    def __init__(
        self,
        backgrounds: list[Background],
        conditions: list[Any],
        settings: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(settings)
        self._backgrounds = backgrounds
        self._conditions = conditions
        self._current_index = 0
        self._last_minute: int | None = None
        self._transition_duration = 1.0
        self._prev_index: int | None = None
        self._transition_elapsed = 0.0
        self._last_dt = 0.0
        self._locked = False
        self._tag_filter = ""

    def _active_indices(self, now=None) -> list[int]:
        if now is None:
            now = datetime.now()
        t = now.time()
        indices = []
        for i, cond in enumerate(self._conditions):
            if cond is None or cond.matches(t):
                if self._tag_filter:
                    bg = self._backgrounds[i]
                    effect_name = getattr(bg, "_effect_name", "")
                    from ..backgrounds.procedural import EFFECTS

                    effect = EFFECTS.get(effect_name)
                    if effect and self._tag_filter not in effect.tags:
                        continue
                indices.append(i)
        return indices if indices else list(range(len(self._backgrounds)))

    def set_active_index(self, index: int) -> None:
        if 0 <= index < len(self._backgrounds):
            self._prev_index = self._current_index
            self._current_index = index
            self._last_minute = datetime.now().minute
            self._transition_elapsed = 0.0
            name = getattr(
                self._backgrounds[index],
                "_effect_name",
                type(self._backgrounds[index]).__name__,
            )
            logger.info("Background -> %s (forced)", name)

    def lock_effect(self, name: str) -> None:
        for i, bg in enumerate(self._backgrounds):
            if getattr(bg, "_effect_name", "") == name:
                self._prev_index = self._current_index
                self._current_index = i
                self._last_minute = datetime.now().minute
                self._transition_elapsed = 0.0
                self._locked = True
                logger.info("Effect locked: %s", name)
                return

    def unlock(self) -> None:
        if self._locked:
            self._locked = False
            self._last_minute = datetime.now().minute
            logger.info("Effect unlocked")

    def set_tag(self, tag: str) -> None:
        self._tag_filter = tag
        self._locked = False
        active = self._active_indices()
        if self._current_index not in active and active:
            self._prev_index = self._current_index
            self._current_index = active[0]
            self._transition_elapsed = 0.0
        logger.info("Tag filter: %s", tag or "(all)")

    @property
    def tag_filter(self) -> str:
        return self._tag_filter

    @property
    def locked(self) -> bool:
        return self._locked

    def update(self, dt: float) -> None:
        if not self._backgrounds:
            return

        self._last_dt = dt

        if self._prev_index is not None:
            self._backgrounds[self._prev_index].update(dt)

        active = self._active_indices()

        if self._current_index not in active:
            self._prev_index = self._current_index
            self._current_index = active[0]
            self._last_minute = datetime.now().minute
            self._transition_elapsed = 0.0
            bg = self._backgrounds[self._current_index]
            name = getattr(bg, "_effect_name", type(bg).__name__)
            logger.info("Background -> %s", name)

        if self._locked:
            self._backgrounds[self._current_index].update(dt)
            return

        now = datetime.now()
        current_minute = now.minute

        if self._last_minute is None:
            self._last_minute = current_minute
        elif current_minute != self._last_minute:
            self._prev_index = self._current_index
            pos = active.index(self._current_index)
            self._current_index = active[(pos + 1) % len(active)]
            self._last_minute = current_minute
            self._transition_elapsed = 0.0
            bg = self._backgrounds[self._current_index]
            name = getattr(bg, "_effect_name", type(bg).__name__)
            logger.info("Background -> %s", name)

        self._backgrounds[self._current_index].update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self._backgrounds:
            return

        if self._prev_index is not None and self._transition_elapsed < self._transition_duration:
            alpha = min(self._transition_elapsed / self._transition_duration, 1.0)

            prev_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            self._backgrounds[self._prev_index].render(prev_surface)
            prev_surface.set_alpha(int(255 * (1.0 - alpha)))
            surface.blit(prev_surface, (0, 0))

            curr_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            self._backgrounds[self._current_index].render(curr_surface)
            curr_surface.set_alpha(int(255 * alpha))
            surface.blit(curr_surface, (0, 0))

            self._transition_elapsed += self._last_dt
        else:
            self._prev_index = None
            self._backgrounds[self._current_index].render(surface)
