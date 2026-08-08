from __future__ import annotations

from wideboy.render.brightness import BrightnessConfig, BrightnessManager


def test_brightness_default_values():
    bg = BrightnessConfig(default=0.5)
    fg = BrightnessConfig(default=0.7)
    mgr = BrightnessManager(background=bg, foreground=fg)
    assert mgr.background_level == 0.5
    assert mgr.foreground_level == 0.7


def test_brightness_defaults():
    mgr = BrightnessManager()
    assert mgr.background_level == 1.0
    assert mgr.foreground_level == 1.0


def test_set_background():
    mgr = BrightnessManager()
    mgr.set_background(0.3)
    assert abs(mgr.background_level - 0.3) < 0.01


def test_set_foreground():
    mgr = BrightnessManager()
    mgr.set_foreground(0.6)
    assert abs(mgr.foreground_level - 0.6) < 0.01


def test_set_background_clamps():
    mgr = BrightnessManager()
    mgr.set_background(1.5)
    assert mgr.background_level == 1.0
    mgr.set_background(-0.5)
    assert mgr.background_level == 0.0


def test_clear_override():
    mgr = BrightnessManager()
    mgr.set_foreground(0.5)
    assert mgr.has_fg_override is True
    mgr.set_foreground(None)
    assert mgr.has_fg_override is False
