from wideboy.config import Settings, load_settings


def test_default_settings():
    s = Settings()
    assert s.display.canvas.width == 768
    assert s.display.canvas.height == 64
    assert s.display.matrix.driver.rows == 64
    assert s.display.matrix.driver.cols == 128
    assert s.display.matrix.driver.chain == 2
    assert s.display.matrix.driver.parallel == 3
    assert s.display.matrix.remap.output_order == [0, 1, 2]
    assert s.general.fps == 30


def test_load_settings_from_yaml(tmp_path):
    (tmp_path / "settings.yml").write_text(
        "general:\n  log_level: debug\n  fps: 60\ndisplay:\n  matrix:\n    enabled: true\n"
    )
    s = load_settings(base_dir=tmp_path, settings_files=["settings.yml"])
    assert s.general.log_level == "debug"
    assert s.general.fps == 60
    assert s.display.matrix.enabled is True


def test_load_settings_deep_merge(tmp_path):
    (tmp_path / "settings.yml").write_text("general:\n  log_level: info\n")
    (tmp_path / "settings.local.yml").write_text("general:\n  fps: 25\n")
    s = load_settings(
        base_dir=tmp_path,
        settings_files=["settings.yml", "settings.local.yml"],
    )
    assert s.general.log_level == "info"
    assert s.general.fps == 25
