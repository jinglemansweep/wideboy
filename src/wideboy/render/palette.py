from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

Color = tuple[float, float, float]

BUILTIN_PALETTES: dict[str, dict[str, list[int]]] = {
    "neon": {
        "primary": [0, 220, 255],
        "secondary": [255, 0, 200],
        "accent": [255, 220, 0],
        "highlight": [255, 255, 255],
        "dim": [10, 10, 40],
    },
    "ocean": {
        "primary": [0, 120, 200],
        "secondary": [0, 200, 180],
        "accent": [100, 220, 255],
        "highlight": [200, 240, 255],
        "dim": [5, 15, 40],
    },
    "sunset": {
        "primary": [255, 80, 40],
        "secondary": [255, 160, 50],
        "accent": [255, 50, 120],
        "highlight": [255, 240, 180],
        "dim": [40, 10, 30],
    },
    "forest": {
        "primary": [40, 180, 60],
        "secondary": [100, 200, 40],
        "accent": [200, 220, 50],
        "highlight": [220, 255, 200],
        "dim": [10, 30, 10],
    },
    "mono": {
        "primary": [200, 200, 200],
        "secondary": [140, 140, 140],
        "accent": [240, 240, 240],
        "highlight": [255, 255, 255],
        "dim": [20, 20, 20],
    },
}


@dataclass
class Palette:
    primary: Color = (0.0, 220.0, 255.0)
    secondary: Color = (255.0, 0.0, 200.0)
    accent: Color = (255.0, 220.0, 0.0)
    highlight: Color = (255.0, 255.0, 255.0)
    dim: Color = (10.0, 10.0, 40.0)

    @classmethod
    def lerp(cls, a: Palette, b: Palette, t: float) -> Palette:
        t = max(0.0, min(1.0, t))
        return cls(
            primary=_lerp_color(a.primary, b.primary, t),
            secondary=_lerp_color(a.secondary, b.secondary, t),
            accent=_lerp_color(a.accent, b.accent, t),
            highlight=_lerp_color(a.highlight, b.highlight, t),
            dim=_lerp_color(a.dim, b.dim, t),
        )

    def sample(self, t: float) -> Color:
        t = max(0.0, min(1.0, t))
        stops = [self.dim, self.primary, self.accent, self.secondary, self.highlight]
        idx = t * (len(stops) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(stops) - 1)
        frac = idx - lo
        return _lerp_color(stops[lo], stops[hi], frac)


def _lerp_color(a: Color, b: Color, t: float) -> Color:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
    )


def parse_palette(data: dict[str, Any]) -> Palette:
    def _c(name: str) -> Color:
        v = data.get(name, [0, 0, 0])
        return (float(v[0]), float(v[1]), float(v[2]))

    return Palette(
        primary=_c("primary"),
        secondary=_c("secondary"),
        accent=_c("accent"),
        highlight=_c("highlight"),
        dim=_c("dim"),
    )


def load_palettes(path: str | Path) -> dict[str, Palette]:
    import yaml

    filepath = Path(path)
    result = {}

    for name, raw in BUILTIN_PALETTES.items():
        result[name] = parse_palette(raw)

    if not filepath.exists():
        logger.debug("Palettes file not found: %s, using built-ins only", path)
        return result

    with open(filepath) as f:
        data = yaml.safe_load(f) or {}

    for name, raw in (data.get("palettes") or {}).items():
        result[name] = parse_palette(raw)

    return result


def _parse_time(s: str) -> time:
    parts = s.split(":")
    return time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)


@dataclass
class PaletteRule:
    after: time | None = None
    before: time | None = None
    palette: str = ""

    def matches(self, now: time) -> bool:
        if self.after is None and self.before is None:
            return True
        if self.after is not None and self.before is not None:
            if self.after <= self.before:
                return self.after <= now <= self.before
            return now >= self.after or now <= self.before
        if self.after is not None:
            return now >= self.after
        return now <= self.before

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PaletteRule:
        return cls(
            after=_parse_time(data["after"]) if "after" in data else None,
            before=_parse_time(data["before"]) if "before" in data else None,
            palette=data.get("palette", ""),
        )


@dataclass
class PaletteConfig:
    default: str = ""
    rules: list[PaletteRule] = field(default_factory=list)
    fade_seconds: float = 3.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PaletteConfig:
        if not data:
            return cls()
        return cls(
            default=data.get("default", ""),
            rules=[PaletteRule.from_dict(r) for r in data.get("rules", [])],
            fade_seconds=float(data.get("fade_seconds", 3.0)),
        )

    def with_default(self, name: str) -> PaletteConfig:
        return PaletteConfig(
            default=name,
            rules=self.rules,
            fade_seconds=self.fade_seconds,
        )


class PaletteClock:
    def __init__(
        self,
        definitions: dict[str, Palette],
        config: PaletteConfig,
    ) -> None:
        self._definitions = definitions
        self._config = config
        self._rule_target = ""
        self._blend = 0.0
        self._initialized = False

    def _target_for_time(self, now: time) -> str:
        for rule in self._config.rules:
            if rule.matches(now) and rule.palette:
                return rule.palette
        return ""

    def _resolve_by_name(self, name: str) -> Palette:
        if name in self._definitions:
            return self._definitions[name]
        logger.warning("Palette '%s' not found, using built-in neon", name)
        return parse_palette(BUILTIN_PALETTES["neon"])

    def update(self, dt: float = 0.0, now: datetime | None = None) -> None:
        if now is None:
            now = datetime.now()

        if not self._initialized:
            self._initialized = True
            target = self._target_for_time(now.time())
            if target:
                self._rule_target = target
                self._blend = 1.0
            return

        target = self._target_for_time(now.time())
        if target != self._rule_target:
            self._rule_target = target

        fade = max(0.1, self._config.fade_seconds)
        if self._rule_target:
            self._blend = min(1.0, self._blend + dt / fade)
        else:
            self._blend = max(0.0, self._blend - dt / fade)

    def resolve(self, base_name: str) -> Palette:
        base = self._resolve_by_name(base_name or self._config.default)
        if self._blend <= 0.0 or not self._rule_target:
            return base
        target = self._resolve_by_name(self._rule_target)
        if self._blend >= 1.0:
            return target
        return Palette.lerp(base, target, self._blend)

    @property
    def blend(self) -> float:
        return self._blend


class PaletteResolver:
    def __init__(
        self,
        definitions: dict[str, Palette],
        config: PaletteConfig,
    ) -> None:
        self._clock = PaletteClock(definitions, config)
        self._base_name = config.default

    def update(self, dt: float, now: datetime | None = None) -> None:
        self._clock.update(dt, now)

    @property
    def palette(self) -> Palette:
        return self._clock.resolve(self._base_name)
