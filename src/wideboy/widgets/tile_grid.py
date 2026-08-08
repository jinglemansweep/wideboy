from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pygame

from ..core.layer import Layer
from ..render.icons import render_icon
from ..render.text import render_text

logger = logging.getLogger(__name__)

TILE_WIDTH = 64
TILE_HEIGHT = 13
ICON_WIDTH = 15
ICON_HEIGHT = 14

LABEL_FONT = "fonts/bitstream-vera.ttf"
LABEL_FONT_SIZE = 11

NOT_APPLICABLE = "N/A"
_UNDEFINED_STATES = {"unavailable", "unknown", "none", ""}
_TRUTHY_STATES = {"on", "true", "yes", "open", "home"}
_FALSY_STATES = {"off", "false", "no", "closed", "not_home"}


def _is_defined(raw: str | None) -> bool:
    return raw is not None and raw.lower() not in _UNDEFINED_STATES


def _is_truthy(raw: str | None) -> bool:
    return raw is not None and raw.lower() in _TRUTHY_STATES


def _is_falsy(raw: str | None) -> bool:
    return raw is not None and raw.lower() in _FALSY_STATES


def _parse_numeric(raw: str | None) -> float | None:
    if not _is_defined(raw):
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def _days_until(timestamp: float) -> int:
    return int(abs(int(datetime.now().timestamp() - timestamp) / 86400))


class Tile:
    def __init__(
        self,
        entity_id: str,
        icon: int | None = None,
        label: str | None = None,
        label_template: str = "{value}",
        visible_when: str = "always",
        visible_attribute: str = "state",
        threshold: float | None = None,
        color_bg: tuple[int, ...] = (16, 16, 16, 192),
        color_fg: tuple[int, ...] = (255, 255, 255, 255),
        color_outline: tuple[int, ...] = (0, 0, 0, 255),
        color_icon_bg: tuple[int, ...] = (32, 32, 32, 255),
        color_icon_fg: tuple[int, ...] = (255, 255, 255, 255),
        color_bg_alert: tuple[int, ...] | None = None,
        color_icon_bg_alert: tuple[int, ...] | None = None,
    ) -> None:
        self.entity_id = entity_id
        self.icon = icon
        self.label = label
        self.label_template = label_template
        self.visible_when = visible_when
        self.visible_attribute = visible_attribute
        self.threshold = threshold
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.color_icon_bg = color_icon_bg
        self.color_icon_fg = color_icon_fg
        self.color_bg_alert = color_bg_alert
        self.color_icon_bg_alert = color_icon_bg_alert

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Tile:
        valid = {k for k in cls.__init__.__code__.co_varnames if k != "self"}
        return cls(**{k: v for k, v in d.items() if k in valid})

    def is_visible(self, raw_state: str | None) -> bool:
        match self.visible_when:
            case "always":
                return True
            case "defined":
                return _is_defined(raw_state)
            case "on":
                return _is_truthy(raw_state)
            case "off":
                return _is_falsy(raw_state)
            case "below":
                v = _parse_numeric(raw_state)
                return v is not None and v < self.threshold
            case "above":
                v = _parse_numeric(raw_state)
                return v is not None and v > self.threshold
            case "days_until":
                v = _parse_numeric(raw_state)
                return (
                    v is not None
                    and self.threshold is not None
                    and _days_until(v) < self.threshold
                )
            case _:
                return True

    def is_alert(self, raw_state: str | None) -> bool:
        if self.visible_when == "below" and self.color_bg_alert:
            v = _parse_numeric(raw_state)
            return v is not None and v >= self.threshold
        if self.visible_when == "above" and self.color_bg_alert:
            v = _parse_numeric(raw_state)
            return v is not None and v <= self.threshold
        return False


class TileGridWidget(Layer):
    def __init__(
        self,
        columns: list[list[Tile]],
        position: tuple[int, int] = (0, 0),
        z_order: int = 10,
    ) -> None:
        super().__init__(position=position, z_order=z_order)
        self.columns = columns
        self.ha_state: dict[str, dict[str, Any]] = {}
        self._tile_cache: dict[str, pygame.Surface] = {}
        self._prev_visible: dict[str, bool] = {}

    def _surface_size(self) -> tuple[int, int] | None:
        return self.content_size

    @property
    def all_tiles(self) -> list[Tile]:
        return [t for col in self.columns for t in col]

    @property
    def content_size(self) -> tuple[int, int]:
        w = len(self.columns) * TILE_WIDTH
        h = max((len(col) * TILE_HEIGHT for col in self.columns), default=0)
        return (w, h)

    def set_state(self, state: dict[str, dict[str, Any]]) -> None:
        changed = False
        for tile in self.all_tiles:
            new = state.get(tile.entity_id, {})
            old = self.ha_state.get(tile.entity_id, {})
            if new != old:
                self.ha_state[tile.entity_id] = new
                self._tile_cache.pop(tile.entity_id, None)
                changed = True
            raw = new.get(tile.visible_attribute) if isinstance(new, dict) else None
            vis = tile.is_visible(str(raw) if raw is not None else None)
            if vis != self._prev_visible.get(tile.entity_id, True):
                self._prev_visible[tile.entity_id] = vis
                changed = True
        if changed:
            self.mark_dirty()

    def _get_raw_state(self, tile: Tile) -> str | None:
        entity_data = self.ha_state.get(tile.entity_id, {})
        raw = entity_data.get(tile.visible_attribute) if isinstance(entity_data, dict) else None
        if raw is not None and str(raw).lower() in _UNDEFINED_STATES:
            return None
        return raw

    def _render_tile(self, tile: Tile) -> pygame.Surface:
        raw = self._get_raw_state(tile)
        alert = tile.is_alert(raw)

        bg = tile.color_bg_alert if alert and tile.color_bg_alert else tile.color_bg
        icon_bg = (
            tile.color_icon_bg_alert
            if alert and tile.color_icon_bg_alert
            else tile.color_icon_bg
        )

        surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        surface.fill(pygame.Color(*bg))

        cx = 0
        if tile.icon is not None:
            icon_surf = render_icon(
                ICON_WIDTH,
                ICON_HEIGHT,
                tile.icon,
                pygame.Color(*icon_bg),
                pygame.Color(*tile.color_icon_fg),
                color_outline=pygame.Color(0, 0, 0, 255),
            )
            surface.blit(icon_surf, (0, 0))
            cx = ICON_WIDTH

        if tile.label is not None:
            label_text = tile.label
        elif raw is not None:
            try:
                numeric = float(raw)
                value: str | float = int(numeric) if numeric == int(numeric) else numeric
            except (ValueError, TypeError, OverflowError):
                value = raw
            try:
                label_text = tile.label_template.format(value=value)
            except Exception:
                label_text = str(raw)
        else:
            label_text = NOT_APPLICABLE

        label_surf = render_text(
            label_text,
            LABEL_FONT,
            LABEL_FONT_SIZE,
            color_fg=pygame.Color(*tile.color_fg),
            color_outline=pygame.Color(*tile.color_outline),
        )
        surface.blit(label_surf, (cx, -1))
        return surface

    def _render(self, surface: pygame.Surface) -> None:
        x = 0
        for column in self.columns:
            y = 0
            for tile in column:
                raw = self._get_raw_state(tile)
                if not tile.is_visible(raw):
                    continue
                if tile.entity_id not in self._tile_cache:
                    self._tile_cache[tile.entity_id] = self._render_tile(tile)
                surface.blit(self._tile_cache[tile.entity_id], (x, y))
                y += TILE_HEIGHT
            x += TILE_WIDTH
