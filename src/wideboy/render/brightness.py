from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BrightnessConfig:
    default: float = 1.0


class BrightnessManager:
    def __init__(
        self,
        background: BrightnessConfig | None = None,
        foreground: BrightnessConfig | None = None,
    ) -> None:
        bg_cfg = background or BrightnessConfig()
        fg_cfg = foreground or BrightnessConfig()
        self._bg_level = bg_cfg.default
        self._fg_level = fg_cfg.default
        self._bg_target = bg_cfg.default
        self._fg_target = fg_cfg.default
        self._bg_override: float | None = None
        self._fg_override: float | None = None

    @property
    def background_level(self) -> float:
        return self._bg_level

    @property
    def foreground_level(self) -> float:
        return self._fg_level

    def set_background(self, level: float | None) -> None:
        if level is None:
            self._bg_override = None
            return
        self._bg_override = max(0.0, min(1.0, level))
        self._bg_level = self._bg_override

    def set_foreground(self, level: float | None) -> None:
        if level is None:
            self._fg_override = None
            return
        self._fg_override = max(0.0, min(1.0, level))
        self._fg_level = self._fg_override

    @property
    def has_bg_override(self) -> bool:
        return self._bg_override is not None

    @property
    def has_fg_override(self) -> bool:
        return self._fg_override is not None

    def update(self, dt: float) -> None:
        pass
