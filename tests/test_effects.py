from wideboy.backgrounds.procedural import (
    EFFECTS,
    Effect,
    get_all_tags,
    get_effect_metadata,
    get_effects_by_tags,
)


def test_all_effects_have_metadata():
    for name, effect in EFFECTS.items():
        assert isinstance(effect, Effect)
        assert effect.name == name
        assert isinstance(effect.default_palette, str)
        assert len(effect.default_palette) > 0
        assert isinstance(effect.tags, tuple)
        assert len(effect.tags) > 0


def test_effects_count():
    assert len(EFFECTS) == 22


def test_get_effects_by_tags_empty():
    result = get_effects_by_tags([])
    assert len(result) == 22


def test_get_effects_by_tags_none():
    result = get_effects_by_tags(None)
    assert len(result) == 22


def test_get_effects_by_tags_retro():
    result = get_effects_by_tags(["retro"])
    assert "matrix" in result
    assert "tetris" in result
    assert "asteroids" in result
    assert "plasma" not in result


def test_get_effects_by_tags_or_match():
    result = get_effects_by_tags(["game", "liquid"])
    assert "breakout" in result
    assert "tetris" in result
    assert "asteroids" in result
    assert "slosh" in result
    assert "plasma" not in result


def test_get_effects_by_tags_nonexistent():
    result = get_effects_by_tags(["nonexistent_tag"])
    assert len(result) == 0


def test_get_effect_metadata():
    meta = get_effect_metadata()
    assert len(meta) == 22
    names = [m["name"] for m in meta]
    assert "plasma" in names
    plasma_meta = next(m for m in meta if m["name"] == "plasma")
    assert plasma_meta["default_palette"] == "neon"
    assert "abstract" in plasma_meta["tags"]
    assert "calm" in plasma_meta["tags"]


def test_get_all_tags():
    tags = get_all_tags()
    assert isinstance(tags, list)
    assert "retro" in tags
    assert "calm" in tags
    assert "energetic" in tags
    assert "game" in tags
    assert len(tags) >= 10


def test_specific_effect_metadata():
    from wideboy.backgrounds.procedural.starfield import starfield
    assert starfield.name == "starfield"
    assert starfield.default_palette == "mono"
    assert "particle" in starfield.tags
    assert "dark" in starfield.tags

    from wideboy.backgrounds.procedural.slosh import slosh
    assert slosh.name == "slosh"
    assert slosh.default_palette == "ocean"
    assert "liquid" in slosh.tags
