from datetime import datetime, time

from wideboy.render.palette import (
    Palette,
    PaletteClock,
    PaletteConfig,
    PaletteResolver,
    PaletteRule,
    load_palettes,
    parse_palette,
)


def test_parse_palette():
    data = {
        "primary": [10, 20, 30],
        "secondary": [40, 50, 60],
        "accent": [70, 80, 90],
        "highlight": [100, 110, 120],
        "dim": [1, 2, 3],
    }
    p = parse_palette(data)
    assert p.primary == (10.0, 20.0, 30.0)
    assert p.dim == (1.0, 2.0, 3.0)


def test_palette_lerp():
    a = Palette(primary=(0, 0, 0))
    b = Palette(primary=(100, 200, 50))
    mid = Palette.lerp(a, b, 0.5)
    assert mid.primary == (50.0, 100.0, 25.0)


def test_palette_sample():
    p = Palette(
        primary=(100, 0, 0),
        secondary=(0, 100, 0),
        accent=(0, 0, 100),
        highlight=(255, 255, 255),
        dim=(0, 0, 0),
    )
    start = p.sample(0.0)
    assert start == (0.0, 0.0, 0.0)
    end = p.sample(1.0)
    assert end == (255.0, 255.0, 255.0)


def test_rule_matches_after():
    rule = PaletteRule(after=time(21, 0), palette="muted")
    assert rule.matches(time(22, 0))
    assert rule.matches(time(21, 0))
    assert not rule.matches(time(20, 0))


def test_rule_matches_before():
    rule = PaletteRule(before=time(7, 0), palette="muted")
    assert rule.matches(time(6, 0))
    assert rule.matches(time(7, 0))
    assert not rule.matches(time(8, 0))


def test_rule_matches_overnight_wrap():
    rule = PaletteRule(after=time(21, 0), before=time(7, 0), palette="muted")
    assert rule.matches(time(22, 0))
    assert rule.matches(time(6, 0))
    assert rule.matches(time(0, 0))
    assert not rule.matches(time(12, 0))
    assert not rule.matches(time(20, 0))


def test_rule_matches_daytime_range():
    rule = PaletteRule(after=time(9, 0), before=time(17, 0), palette="day")
    assert rule.matches(time(12, 0))
    assert not rule.matches(time(8, 0))
    assert not rule.matches(time(18, 0))


def test_resolver_default():
    defs = {"neon": Palette(primary=(1, 2, 3))}
    config = PaletteConfig(default="neon", fade_seconds=1.0)
    resolver = PaletteResolver(definitions=defs, config=config)
    resolver.update(0.1, datetime(2026, 1, 1, 12, 0))
    assert resolver.palette.primary == (1.0, 2.0, 3.0)


def test_resolver_switches_on_rule():
    neon = Palette(primary=(0, 0, 255))
    muted = Palette(primary=(30, 30, 30))
    defs = {"neon": neon, "muted": muted}
    config = PaletteConfig(
        default="neon",
        rules=[PaletteRule(after=time(21, 0), palette="muted")],
        fade_seconds=2.0,
    )
    resolver = PaletteResolver(definitions=defs, config=config)

    resolver.update(0.0, datetime(2026, 1, 1, 12, 0))
    assert resolver.palette.primary == (0.0, 0.0, 255.0)

    resolver.update(0.0, datetime(2026, 1, 1, 21, 0))
    resolver.update(0.1, datetime(2026, 1, 1, 21, 0))
    assert resolver.palette.primary != (0.0, 0.0, 255.0)

    resolver.update(2.0, datetime(2026, 1, 1, 21, 0))
    assert resolver.palette.primary == (30.0, 30.0, 30.0)


def test_resolver_crossfade():
    a = Palette(primary=(0, 0, 0))
    b = Palette(primary=(100, 100, 100))
    defs = {"a": a, "b": b}
    config = PaletteConfig(
        default="a",
        rules=[PaletteRule(after=time(21, 0), palette="b")],
        fade_seconds=2.0,
    )
    resolver = PaletteResolver(definitions=defs, config=config)

    resolver.update(0.0, datetime(2026, 1, 1, 12, 0))
    assert resolver.palette.primary == (0.0, 0.0, 0.0)

    resolver.update(0.0, datetime(2026, 1, 1, 21, 0))
    assert resolver.palette.primary == (0.0, 0.0, 0.0)

    resolver.update(1.0, datetime(2026, 1, 1, 21, 0))
    r, g, b = resolver.palette.primary
    assert 40.0 < r < 60.0

    resolver.update(1.0, datetime(2026, 1, 1, 21, 0))
    assert resolver.palette.primary == (100.0, 100.0, 100.0)


def test_load_palettes_with_builtins(tmp_path):
    palettes = load_palettes(tmp_path / "nonexistent.yml")
    assert "neon" in palettes
    assert "ocean" in palettes


def test_load_palettes_from_file(tmp_path):
    (tmp_path / "palettes.yml").write_text(
        "palettes:\n  custom:\n    primary: [1, 2, 3]\n"
        "    secondary: [4, 5, 6]\n    accent: [7, 8, 9]\n"
        "    highlight: [10, 11, 12]\n    dim: [0, 0, 0]\n"
    )
    palettes = load_palettes(tmp_path / "palettes.yml")
    assert "custom" in palettes
    assert palettes["custom"].primary == (1.0, 2.0, 3.0)
    assert "neon" in palettes


def test_shared_clock_no_flash_on_effect_change():
    from wideboy.core.factory import _SharedClockResolver

    neon = Palette(primary=(0, 220, 255))
    muted = Palette(primary=(30, 30, 30))
    defs = {"neon": neon, "ocean": Palette(primary=(0, 120, 200)), "muted": muted}
    config = PaletteConfig(
        default="neon",
        rules=[PaletteRule(after=time(21, 0), palette="muted")],
        fade_seconds=3.0,
    )
    clock = PaletteClock(definitions=defs, config=config)

    resolver_neon = _SharedClockResolver(clock, "neon")
    resolver_ocean = _SharedClockResolver(clock, "ocean")

    resolver_neon.update(0.0, datetime(2026, 1, 1, 22, 0))

    assert resolver_neon.palette.primary == (30.0, 30.0, 30.0)
    assert resolver_ocean.palette.primary == (30.0, 30.0, 30.0)
