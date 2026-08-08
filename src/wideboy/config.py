from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class GeneralConfig(BaseModel):
    log_level: str = "info"
    fps: int = 30


class CanvasConfig(BaseModel):
    width: int = 768
    height: int = 64


class DriverConfig(BaseModel):
    gpio_mapping: str = "regular"
    rows: int = 64
    cols: int = 128
    chain: int = 2
    parallel: int = 3
    multiplexing: int = 0
    pixel_mapper: str = ""
    pwm_bits: int = 8
    brightness: int = 50
    scan_mode: int = 0
    row_addr_type: int = 0
    show_refresh: bool = False
    rgb_sequence: str = "RGB"
    pwm_lsb_nanoseconds: int = 200
    pwm_dither_bits: int = 0
    no_hardware_pulse: bool = False
    panel_type: str | None = None
    slowdown_gpio: int = 4
    daemon: bool = False
    no_drop_privs: bool = True


class RemapConfig(BaseModel):
    output_order: list[int] = Field(default_factory=lambda: [0, 1, 2])


class MatrixConfig(BaseModel):
    enabled: bool = False
    driver: DriverConfig = Field(default_factory=DriverConfig)
    remap: RemapConfig = Field(default_factory=RemapConfig)


class DisplayConfig(BaseModel):
    canvas: CanvasConfig = Field(default_factory=CanvasConfig)
    matrix: MatrixConfig = Field(default_factory=MatrixConfig)


class HomeAssistantConfig(BaseModel):
    host: str = ""
    port: int = 8123
    token: str = ""
    ssl: bool = False


class ScenesConfig(BaseModel):
    file: str = "scenes/default.yml"


class PathsConfig(BaseModel):
    backgrounds: str = "assets/backgrounds"
    fonts: str = "fonts"


class BrightnessScheduleConfig(BaseModel):
    default: float = 1.0


class BrightnessConfig(BaseModel):
    background: BrightnessScheduleConfig = Field(default_factory=BrightnessScheduleConfig)
    foreground: BrightnessScheduleConfig = Field(default_factory=BrightnessScheduleConfig)


class MqttConfig(BaseModel):
    enabled: bool = False
    host: str = ""
    port: int = 1883
    username: str = ""
    password: str = ""
    discovery_prefix: str = "homeassistant"
    device_id: str = "wideboy"
    device_name: str = "Wideboy LED Display"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WIDEBOY_",
        env_nested_delimiter="__",
    )

    general: GeneralConfig = Field(default_factory=GeneralConfig)
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    homeassistant: HomeAssistantConfig = Field(default_factory=HomeAssistantConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    scenes: ScenesConfig = Field(default_factory=ScenesConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    brightness: BrightnessConfig = Field(default_factory=BrightnessConfig)
    effect_tags: dict[str, list[str]] = Field(default_factory=dict)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    import yaml

    with open(path) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_settings(
    base_dir: Path | None = None,
    settings_files: list[str] | None = None,
) -> Settings:
    if base_dir is None:
        base_dir = Path.cwd()
    if settings_files is None:
        settings_files = ["settings.yml", "settings.local.yml", "secrets.yml"]

    merged: dict[str, Any] = {}
    for filename in settings_files:
        filepath = base_dir / filename
        if filepath.exists():
            logger.debug("Loading config from %s", filepath)
            merged = _deep_merge(merged, _load_yaml_file(filepath))

    return Settings(**merged)
