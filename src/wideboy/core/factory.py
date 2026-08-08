from __future__ import annotations

import logging

from ..backgrounds.base import Background
from ..backgrounds.composite import CompositeBackground
from ..backgrounds.gif import GifBackground
from ..backgrounds.image import ImageBackground
from ..backgrounds.slideshow import SlideshowBackground
from ..core.scene import SceneDef
from ..render.palette import Palette, PaletteClock
from ..widgets.clock import ClockWidget
from ..widgets.tile_grid import Tile, TileGridWidget

logger = logging.getLogger(__name__)


def _get_background_types() -> dict[str, type[Background]]:
    types: dict[str, type[Background]] = {
        "image": ImageBackground,
        "slideshow": SlideshowBackground,
        "gif": GifBackground,
    }
    try:
        from ..backgrounds.procedural import ProceduralBackground

        types["procedural"] = ProceduralBackground
    except ImportError:
        logger.debug("Procedural backgrounds unavailable (numpy missing)")
    return types


def _build_tile_grid(position, settings: dict) -> TileGridWidget:
    raw_columns = settings.get("columns", [])
    columns = []
    for col_tiles in raw_columns:
        columns.append([Tile.from_dict(t) for t in col_tiles])
    return TileGridWidget(columns=columns, position=position)


def build_background(
    scene: SceneDef,
    palette_definitions: dict[str, Palette] | None = None,
) -> Background:
    bg_types = _get_background_types()
    defs = palette_definitions or {}
    clock = PaletteClock(definitions=defs, config=scene.palette_config)

    backgrounds = []
    conditions = []
    for bg_def in scene.backgrounds:
        cls = bg_types.get(bg_def.type, ImageBackground)
        if bg_def.type == "procedural":
            settings = bg_def.settings.copy()
            effect_palette = settings.pop("palette", None)

            if bg_def.tags is not None:
                from ..backgrounds.procedural import get_effects_by_tags

                matched = get_effects_by_tags(bg_def.tags)
                for effect_name, effect in matched.items():
                    s = {"effect": effect_name, "speed": settings.get("speed", 1.0)}
                    palette_name = effect_palette or effect.default_palette
                    resolver = _SharedClockResolver(clock, palette_name)
                    s["_palette_resolver"] = resolver
                    backgrounds.append(cls(settings=s))
                    conditions.append(bg_def.condition)
            else:
                effect_name = settings.get("effect", "plasma")
                if not effect_palette:
                    from ..backgrounds.procedural import EFFECTS

                    effect = EFFECTS.get(effect_name)
                    if effect and hasattr(effect, "default_palette"):
                        effect_palette = effect.default_palette
                    else:
                        effect_palette = scene.palette_config.default
                resolver = _SharedClockResolver(clock, effect_palette)
                settings["_palette_resolver"] = resolver
                backgrounds.append(cls(settings=settings))
                conditions.append(bg_def.condition)
        else:
            backgrounds.append(cls(settings=bg_def.settings))
            conditions.append(bg_def.condition)

    if len(backgrounds) == 1:
        return backgrounds[0]
    return CompositeBackground(backgrounds=backgrounds, conditions=conditions)


class _SharedClockResolver:
    def __init__(self, clock: PaletteClock, base_name: str) -> None:
        self._clock = clock
        self._base_name = base_name

    def update(self, dt: float, now=None) -> None:
        self._clock.update(dt, now)

    def set_base_name(self, name: str) -> None:
        self._base_name = name

    @property
    def base_name(self) -> str:
        return self._base_name

    @property
    def palette(self) -> Palette:
        return self._clock.resolve(self._base_name)


def _resolve_position(
    position: tuple[int, int],
    anchor: str,
    canvas_width: int,
    canvas_height: int,
    content_width: int = 0,
    content_height: int = 0,
) -> tuple[int, int]:
    x, y = position
    match anchor:
        case "top-right":
            x = canvas_width - x - content_width
        case "bottom-left":
            y = canvas_height - y - content_height
        case "bottom-right":
            x = canvas_width - x - content_width
            y = canvas_height - y - content_height
    return (x, y)


def build_widgets(
    scene: SceneDef,
    canvas_width: int = 768,
    canvas_height: int = 64,
) -> list:
    widgets = []
    for wdef in scene.widgets:
        if wdef.type == "clock":
            widget = ClockWidget(position=(0, 0), settings=wdef.settings)
        elif wdef.type == "tile_grid":
            widget = _build_tile_grid((0, 0), wdef.settings)
        else:
            logger.warning("Unknown widget type: %s", wdef.type)
            continue
        cw, ch = getattr(widget, "content_size", (0, 0))
        widget.position = _resolve_position(
            wdef.position, wdef.anchor, canvas_width, canvas_height, cw, ch
        )
        widgets.append(widget)
    return widgets


def collect_entity_ids(scene: SceneDef) -> list[str]:
    ids: list[str] = list(scene.homeassistant_entities)
    for wdef in scene.widgets:
        if wdef.type == "tile_grid":
            for col_tiles in wdef.settings.get("columns", []):
                for t in col_tiles:
                    eid = t.get("entity_id")
                    if eid and eid not in ids:
                        ids.append(eid)
    return ids
