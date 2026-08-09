from wideboy.core.scene import SceneDef, load_scene


def test_load_default_scene():
    scene = load_scene("scenes/default.yml")
    assert isinstance(scene, SceneDef)
    assert scene.metadata.get("name") == "default"


def test_load_missing_scene():
    scene = load_scene("/nonexistent/scene.yml")
    assert isinstance(scene, SceneDef)
    assert len(scene.backgrounds) == 0


def test_load_scene_from_yaml(tmp_path):
    (tmp_path / "test.yml").write_text(
        "metadata:\n  name: test\n"
        "background:\n  type: slideshow\n  settings:\n    interval: 30\n"
        "widgets:\n  - type: clock\n    position: [0, 0]\n"
        "homeassistant:\n  entities:\n    - sensor.temp\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    assert scene.metadata["name"] == "test"
    assert len(scene.backgrounds) == 1
    assert scene.backgrounds[0].type == "slideshow"
    assert scene.backgrounds[0].settings["interval"] == 30
    assert len(scene.widgets) == 1
    assert scene.widgets[0].type == "clock"
    assert scene.homeassistant_entities == ["sensor.temp"]


def test_load_scene_with_multiple_backgrounds(tmp_path):
    (tmp_path / "test.yml").write_text(
        "backgrounds:\n"
        "  - type: image\n"
        "    settings:\n      path: bg1.png\n"
        "  - type: slideshow\n"
        "    settings:\n      directory: slides\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    assert len(scene.backgrounds) == 2
    assert scene.backgrounds[0].type == "image"
    assert scene.backgrounds[0].settings["path"] == "bg1.png"
    assert scene.backgrounds[1].type == "slideshow"
    assert scene.backgrounds[1].settings["directory"] == "slides"


def test_scene_palette_config():
    scene = load_scene("scenes/default.yml")
    assert scene.palette_config.default == "neon"
    assert len(scene.palette_config.rules) == 0


def test_per_effect_palette_in_settings(tmp_path):
    (tmp_path / "test.yml").write_text(
        "palette:\n  default: neon\n"
        "backgrounds:\n"
        "  - type: procedural\n"
        "    settings:\n      effect: plasma\n      palette: ocean\n"
        "  - type: procedural\n"
        "    settings:\n      effect: starfield\n      palette: mono\n"
        "  - type: procedural\n"
        "    settings:\n      effect: waves\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    assert len(scene.backgrounds) == 3
    assert scene.backgrounds[0].settings.get("palette") == "ocean"
    assert scene.backgrounds[1].settings.get("palette") == "mono"
    assert scene.backgrounds[2].settings.get("palette") is None


def test_background_conditions(tmp_path):
    (tmp_path / "test.yml").write_text(
        "backgrounds:\n"
        "  - type: procedural\n"
        "    settings:\n      effect: plasma\n"
        '    after: "07:00"\n'
        '    before: "21:00"\n'
        "  - type: procedural\n"
        "    settings:\n      effect: starfield\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    assert scene.backgrounds[0].condition is not None
    assert scene.backgrounds[1].condition is None


def test_composite_background_filters_by_condition():
    from datetime import datetime, time

    from wideboy.backgrounds.base import Background
    from wideboy.backgrounds.composite import CompositeBackground
    from wideboy.render.palette import PaletteRule

    class DummyBg(Background):
        def __init__(self, name):
            super().__init__()
            self.name = name
            self.rendered = False

        def render(self, surface):
            self.rendered = True

    day_rule = PaletteRule(after=time(7, 0), before=time(21, 0))
    bgs = [DummyBg("day_only"), DummyBg("always")]
    conditions = [day_rule, None]
    composite = CompositeBackground(backgrounds=bgs, conditions=conditions)

    active_day = composite._active_indices(datetime(2026, 1, 1, 12, 0))
    assert 0 in active_day
    assert 1 in active_day

    active_night = composite._active_indices(datetime(2026, 1, 1, 22, 0))
    assert 0 not in active_night
    assert 1 in active_night


def test_tags_parsed_from_yaml(tmp_path):
    (tmp_path / "test.yml").write_text(
        "backgrounds:\n"
        "  - type: procedural\n"
        "    tags: [retro, game]\n"
        "  - type: procedural\n"
        "    tags: []\n"
        "  - type: procedural\n"
        "    settings:\n      effect: plasma\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    assert scene.backgrounds[0].tags == ["retro", "game"]
    assert scene.backgrounds[1].tags == []
    assert scene.backgrounds[2].tags is None


def test_default_scene_uses_tags():
    scene = load_scene("scenes/default.yml")
    assert len(scene.backgrounds) == 1
    assert scene.backgrounds[0].tags == []


def test_composite_lock_effect():
    from wideboy.backgrounds.base import Background
    from wideboy.backgrounds.composite import CompositeBackground

    class DummyBg(Background):
        def __init__(self, name):
            super().__init__()
            self._effect_name = name

        def render(self, surface):
            pass

    bgs = [DummyBg("plasma"), DummyBg("aurora"), DummyBg("waves")]
    composite = CompositeBackground(backgrounds=bgs, conditions=[None, None, None])
    assert composite._current_index == 0

    composite.lock_effect("aurora")
    assert composite._current_index == 1
    assert composite.locked is True


def test_composite_unlock():
    from wideboy.backgrounds.base import Background
    from wideboy.backgrounds.composite import CompositeBackground

    class DummyBg(Background):
        def __init__(self, name):
            super().__init__()
            self._effect_name = name

        def render(self, surface):
            pass

    bgs = [DummyBg("plasma"), DummyBg("aurora")]
    composite = CompositeBackground(backgrounds=bgs, conditions=[None, None])
    composite.lock_effect("aurora")
    assert composite.locked is True
    composite.unlock()
    assert composite.locked is False


def test_composite_set_tag():
    from wideboy.backgrounds.base import Background
    from wideboy.backgrounds.composite import CompositeBackground

    class DummyBg(Background):
        def __init__(self, name):
            super().__init__()
            self._effect_name = name

        def render(self, surface):
            pass

    bgs = [DummyBg("plasma"), DummyBg("matrix"), DummyBg("tetris")]
    composite = CompositeBackground(backgrounds=bgs, conditions=[None, None, None])
    composite.set_tag("retro")
    assert composite.tag_filter == "retro"
    active = composite._active_indices()
    assert 0 not in active
    assert 1 in active
    assert 2 in active


def test_tag_expansion_in_factory(tmp_path):
    from wideboy.core.factory import build_background
    from wideboy.core.scene import load_scene
    from wideboy.render.palette import load_palettes

    (tmp_path / "test.yml").write_text(
        "palette:\n  default: neon\nbackgrounds:\n  - type: procedural\n    tags: [liquid]\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    palettes = load_palettes("palettes.yml")
    bg = build_background(scene, palette_definitions=palettes)
    assert hasattr(bg, "_effect_name")
    assert bg._effect_name == "slosh"


def test_tag_expansion_all_effects(tmp_path):
    from wideboy.backgrounds.composite import CompositeBackground
    from wideboy.core.factory import build_background
    from wideboy.core.scene import load_scene
    from wideboy.render.palette import load_palettes

    (tmp_path / "test.yml").write_text(
        "palette:\n  default: neon\nbackgrounds:\n  - type: procedural\n    tags: []\n"
    )
    scene = load_scene(str(tmp_path / "test.yml"))
    palettes = load_palettes("palettes.yml")
    bg = build_background(scene, palette_definitions=palettes)
    assert isinstance(bg, CompositeBackground)
    assert len(bg._backgrounds) == 29
