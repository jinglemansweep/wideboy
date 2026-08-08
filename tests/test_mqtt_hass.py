from __future__ import annotations

import json
from unittest.mock import MagicMock

from wideboy.config import MqttConfig, Settings
from wideboy.services.mqtt_hass import MqttHassService


def _make_state(effect_name: str = "plasma") -> MagicMock:
    state = MagicMock()
    state.master_on = True
    state.master_level = 1.0
    state.brightness = MagicMock()
    state.brightness.foreground_level = 0.8
    state.brightness.background_level = 0.8
    state.brightness.has_bg_override = False
    state.brightness.has_fg_override = False
    state.background = MagicMock()
    state.background._effect_name = effect_name
    state.widgets = []
    return state


def _make_service(effect_name: str = "plasma") -> MqttHassService:
    cfg = MqttConfig(
        enabled=True,
        host="localhost",
        port=1883,
        device_id="test_display",
        device_name="Test Display",
    )
    state = _make_state(effect_name)
    settings = Settings()
    svc = MqttHassService(cfg, state, settings)
    return svc


def test_initial_state():
    svc = _make_service("aurora")
    assert svc._current_state["state"] == "ON"
    assert svc._current_state["brightness"] == 255
    assert svc._current_state["effect"] == "aurora"


def test_device_info():
    svc = _make_service()
    info = svc._device_info()
    assert info["identifiers"] == ["test_display"]
    assert info["name"] == "Test Display"


def test_discovery_payload_light():
    svc = _make_service()
    payload = svc._discovery_payload("light", "light")
    assert payload["~"] == "test_display/light"
    assert payload["unique_id"] == "test_display_light"
    assert payload["brightness"] is True
    assert payload["schema"] == "json"
    assert "availability_topic" in payload


def test_discovery_payload_number():
    svc = _make_service()
    payload = svc._discovery_payload("number", "fg_brightness")
    assert payload["min"] == 0
    assert payload["max"] == 100
    assert payload["step"] == 1
    assert payload["unit_of_measurement"] == "%"


def test_discovery_payload_effect_speed():
    svc = _make_service()
    payload = svc._discovery_payload("number", "effect_speed")
    assert payload["min"] == 0.1
    assert payload["max"] == 5.0


def test_available_effects():
    svc = _make_service()
    effects = svc._get_available_effects()
    assert "plasma" in effects
    assert "aurora" in effects
    assert "auto" in effects
    assert len(effects) == 29


def test_handle_light_on():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command(
        "test_display/light/set",
        json.dumps({"state": "ON", "brightness": 128}),
    )
    assert svc._current_state["state"] == "ON"
    assert svc._current_state["brightness"] == 128
    assert svc._state.master_on is True
    assert abs(svc._state.master_level - 128 / 255) < 0.01


def test_handle_light_off():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command(
        "test_display/light/set",
        json.dumps({"state": "OFF"}),
    )
    assert svc._state.master_on is False


def test_handle_fg_brightness():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/fg_brightness/set", "75")
    assert svc._current_state["fg_brightness"] == 75
    svc._state.brightness.set_foreground.assert_called_once_with(0.75)


def test_handle_effect_speed():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/effect_speed/set", "2.5")
    assert svc._current_state["effect_speed"] == 2.5


def test_handle_invalid_brightness():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/fg_brightness/set", "not_a_number")
    svc._state.brightness.set_foreground.assert_not_called()


def test_handle_invalid_json_light():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/light/set", "not json")
    assert svc._current_state["state"] == "ON"


def test_publish_state_retained():
    svc = _make_service()
    svc._client = MagicMock()
    svc._publish_state("light")
    svc._client.publish.assert_called_once()
    args = svc._client.publish.call_args
    assert args[0][0] == "test_display/light/state"
    assert args[1]["retain"] is True


def test_publish_offline_on_disconnect():
    svc = _make_service()
    svc._client = MagicMock()
    svc._client.publish = MagicMock()
    svc._client.loop_stop = MagicMock()
    svc._client.disconnect = MagicMock()
    import asyncio

    asyncio.run(svc.disconnect())
    first_call = svc._client.publish.call_args_list[0]
    assert first_call[0][0] == "test_display/status"
    assert first_call[0][1] == "offline"


def test_available_tags():
    svc = _make_service()
    tags = svc._get_available_tags()
    assert "all" in tags
    assert "retro" in tags
    assert "calm" in tags


def test_available_palettes():
    svc = _make_service()
    palettes = svc._get_available_palettes()
    assert "neon" in palettes
    assert "ocean" in palettes
    assert "mono" in palettes


def test_handle_tag_command():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/tag/set", "retro")
    assert svc._current_state["tag"] == "retro"


def test_handle_palette_command():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/palette/set", "ocean")
    assert svc._current_state["palette"] == "ocean"


def test_handle_effect_auto():
    svc = _make_service()
    svc._client = MagicMock()
    svc._handle_command("test_display/effect/set", "auto")
    assert svc._current_state["effect"] == "auto"
