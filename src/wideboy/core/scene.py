from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ..render.palette import PaletteConfig, PaletteRule

logger = logging.getLogger(__name__)


@dataclass
class BackgroundDef:
    type: str = "image"
    settings: dict[str, Any] = field(default_factory=dict)
    condition: PaletteRule | None = None
    tags: list[str] | None = None


@dataclass
class WidgetDef:
    type: str = ""
    position: tuple[int, int] = (0, 0)
    anchor: str = "top-left"
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneDef:
    metadata: dict[str, str] = field(default_factory=dict)
    backgrounds: list[BackgroundDef] = field(default_factory=list)
    widgets: list[WidgetDef] = field(default_factory=list)
    homeassistant_entities: list[str] = field(default_factory=list)
    palette_config: PaletteConfig = field(default_factory=PaletteConfig)


def _parse_background(bg_raw: dict[str, Any]) -> BackgroundDef:
    condition = None
    if "after" in bg_raw or "before" in bg_raw:
        condition = PaletteRule.from_dict(bg_raw)
    tags = bg_raw.get("tags")
    if tags is not None and not isinstance(tags, list):
        tags = list(tags)
    return BackgroundDef(
        type=bg_raw.get("type", "image"),
        settings=bg_raw.get("settings", {}),
        condition=condition,
        tags=tags,
    )


def load_scene(path: str) -> SceneDef:
    from pathlib import Path

    import yaml

    filepath = Path(path)
    if not filepath.exists():
        logger.warning("Scene file not found: %s, using defaults", path)
        return SceneDef()

    with open(filepath) as f:
        raw = yaml.safe_load(f) or {}

    if "backgrounds" in raw:
        backgrounds = [_parse_background(b) for b in raw["backgrounds"]]
    elif "background" in raw:
        backgrounds = [_parse_background(raw["background"])]
    else:
        backgrounds = [_parse_background({})]

    widgets = []
    for w in raw.get("widgets", []):
        pos = w.get("position", [0, 0])
        widgets.append(
            WidgetDef(
                type=w.get("type", ""),
                position=(pos[0], pos[1]),
                anchor=w.get("anchor", "top-left"),
                settings=w.get("settings", {}),
            )
        )

    ha = raw.get("homeassistant", {})
    entities = ha.get("entities", [])

    palette_config = PaletteConfig.from_dict(raw.get("palette"))

    return SceneDef(
        metadata=raw.get("metadata", {}),
        backgrounds=backgrounds,
        widgets=widgets,
        homeassistant_entities=entities,
        palette_config=palette_config,
    )
