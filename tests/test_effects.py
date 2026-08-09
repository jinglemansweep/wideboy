import pytest

from wideboy.backgrounds.procedural import (
    EFFECTS,
    Effect,
    get_all_tags,
    get_effect_metadata,
    get_effect_tags,
    get_effects_by_tags,
)
from wideboy.backgrounds.procedural._registry import set_extra_tags


@pytest.fixture(autouse=True)
def _reset_extra_tags():
    set_extra_tags({})
    yield
    set_extra_tags({})


def test_all_effects_have_metadata():
    for name, effect in EFFECTS.items():
        assert isinstance(effect, Effect)
        assert effect.name == name
        assert isinstance(effect.default_palette, str)
        assert len(effect.default_palette) > 0
        assert isinstance(effect.tags, tuple)
        assert len(effect.tags) > 0


def test_effects_count():
    assert len(EFFECTS) == 29


def test_get_effects_by_tags_empty():
    result = get_effects_by_tags([])
    assert len(result) == 29


def test_get_effects_by_tags_none():
    result = get_effects_by_tags(None)
    assert len(result) == 29


def test_get_effects_by_tags_retro():
    result = get_effects_by_tags(["retro"])
    assert "matrix" in result
    assert "tetris" in result
    assert "asteroids" in result
    assert "flappy" in result
    assert "plasma" not in result


def test_get_effects_by_tags_or_match():
    result = get_effects_by_tags(["game", "liquid"])
    assert "breakout" in result
    assert "tetris" in result
    assert "asteroids" in result
    assert "flappy" in result
    assert "slosh" in result
    assert "plasma" not in result


def test_get_effects_by_tags_nonexistent():
    result = get_effects_by_tags(["nonexistent_tag"])
    assert len(result) == 0


def test_get_effect_metadata():
    meta = get_effect_metadata()
    assert len(meta) == 29
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

    from wideboy.backgrounds.procedural.flappy import flappy

    assert flappy.name == "flappy"
    assert flappy.default_palette == "neon"
    assert "game" in flappy.tags
    assert "retro" in flappy.tags


def test_get_effect_tags_no_extra():
    tags = get_effect_tags("plasma")
    assert tags == set(EFFECTS["plasma"].tags)


def test_get_effect_tags_with_extra():
    set_extra_tags({"plasma": ["evening"]})
    tags = get_effect_tags("plasma")
    assert "evening" in tags
    assert "abstract" in tags
    assert "calm" in tags


def test_get_effect_tags_unknown_effect():
    set_extra_tags({"nonexistent": ["foo"]})
    assert get_effect_tags("nonexistent") == {"foo"}


def test_set_extra_tags_replaces():
    set_extra_tags({"plasma": ["evening"]})
    assert "evening" in get_effect_tags("plasma")
    set_extra_tags({"plasma": ["morning"]})
    assert "morning" in get_effect_tags("plasma")
    assert "evening" not in get_effect_tags("plasma")


def test_set_extra_tags_empty_list_ignored():
    set_extra_tags({"plasma": []})
    assert get_effect_tags("plasma") == set(EFFECTS["plasma"].tags)


def test_get_effects_by_tags_with_extra():
    set_extra_tags({"plasma": ["evening"]})
    result = get_effects_by_tags(["evening"])
    assert "plasma" in result
    assert len(result) == 1


def test_get_all_tags_with_extra():
    set_extra_tags({"plasma": ["evening"], "rings": ["evening"]})
    tags = get_all_tags()
    assert "evening" in tags


def test_get_effect_metadata_with_extra():
    set_extra_tags({"plasma": ["custom"]})
    meta = get_effect_metadata()
    plasma_meta = next(m for m in meta if m["name"] == "plasma")
    assert "custom" in plasma_meta["tags"]
    assert "abstract" in plasma_meta["tags"]
