from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import signal
import time
from pathlib import Path
from typing import Any

import pygame

from . import __version__
from .config import Settings, load_settings

os.environ["SDL_VIDEO_CENTERED"] = "1"

logger = logging.getLogger(__name__)


def _setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wideboy", description="RGB LED matrix dashboard")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--backend",
        choices=["emulator", "hardware"],
        default="emulator",
        help="Display backend (default: emulator)",
    )
    parser.add_argument(
        "--test-pattern",
        action="store_true",
        help="Draw labelled colour bars per segment to verify wiring",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Directory containing settings files (default: cwd)",
    )
    return parser


def _create_display(settings, backend: str):
    from .display.emulator import EmulatorDisplay
    from .display.hardware import HardwareDisplay

    if backend == "hardware":
        return HardwareDisplay(settings)
    return EmulatorDisplay(settings)


def _draw_test_pattern(surface: pygame.Surface, settings) -> None:
    from .display.remap import draw_test_pattern

    draw_test_pattern(surface, settings.display.matrix.remap.output_order)


def _start_ha(settings: Settings, entity_ids: list[str]):
    from .services.homeassistant import HomeAssistantService

    ha_cfg = settings.homeassistant
    if not ha_cfg.host or not ha_cfg.token or not entity_ids:
        return None
    svc = HomeAssistantService(
        host=ha_cfg.host,
        port=ha_cfg.port,
        token=ha_cfg.token,
        entity_ids=entity_ids,
        ssl=ha_cfg.ssl,
    )
    svc.start()
    return svc


class DisplayState:
    def __init__(
        self,
        scene: Any,
        palettes: dict,
        background: Any,
        widgets: list,
        brightness: Any,
    ) -> None:
        self.scene = scene
        self.palettes = palettes
        self.background = background
        self.widgets = widgets
        self.brightness = brightness
        self.master_on: bool = True
        self.master_level: float = 1.0
        self.notification: dict | None = None


def _build_scene(settings: Settings):
    from .core.factory import (
        add_system_overlays,
        build_background,
        build_widgets,
        collect_entity_ids,
    )
    from .core.scene import load_scene
    from .render.brightness import BrightnessConfig, BrightnessManager
    from .render.palette import load_palettes

    scene = load_scene(settings.scenes.file)
    palettes = load_palettes("palettes.yml")
    background = build_background(scene, palette_definitions=palettes)
    widgets = build_widgets(
        scene,
        canvas_width=settings.display.canvas.width,
        canvas_height=settings.display.canvas.height,
    )
    brightness = BrightnessManager(
        background=BrightnessConfig(default=settings.brightness.background.default),
        foreground=BrightnessConfig(default=settings.brightness.foreground.default),
    )
    entity_ids = collect_entity_ids(scene)
    state = DisplayState(scene, palettes, background, widgets, brightness)
    add_system_overlays(
        state,
        canvas_width=settings.display.canvas.width,
        canvas_height=settings.display.canvas.height,
    )
    return state, entity_ids


async def run_loop(
    screen: pygame.Surface,
    display: Any,
    state: DisplayState,
    ha_service: Any,
    mqtt_service: Any,
    settings: Settings,
    test_pattern: bool,
    stop_event: asyncio.Event,
) -> None:
    w = settings.display.canvas.width
    h = settings.display.canvas.height
    fps = settings.general.fps
    frame_time = 1.0 / fps
    running = True

    while running and not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if mqtt_service:
            await mqtt_service.drain_commands(state)

        frame_start = time.monotonic()

        if test_pattern:
            _draw_test_pattern(screen, settings)
        elif not state.master_on:
            screen.fill((0, 0, 0))
        else:
            screen.fill((0, 0, 0))

            state.brightness.update(frame_time)

            state.background.update(frame_time)
            state.background.render(screen)

            bg_level = state.brightness.background_level
            if bg_level < 1.0:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, int(255 * (1.0 - bg_level))))
                screen.blit(overlay, (0, 0))

            if ha_service:
                from .widgets.tile_grid import TileGridWidget

                for widget in state.widgets:
                    if isinstance(widget, TileGridWidget):
                        widget.set_state(ha_service.snapshot)

            fg_level = state.brightness.foreground_level
            for widget in state.widgets:
                widget.update(frame_time)
                widget.render(screen, brightness=fg_level)

        display.present(screen)

        elapsed = time.monotonic() - frame_start
        sleep_time = max(0, frame_time - elapsed)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        else:
            await asyncio.sleep(0)


async def async_main(args) -> None:
    settings = load_settings(base_dir=args.config_dir)
    _setup_logging(settings.general.log_level)

    from .backgrounds.procedural._registry import set_extra_tags

    set_extra_tags(settings.effect_tags)

    logger.info("wideboy v%s starting (backend=%s)", __version__, args.backend)

    pygame.init()
    pygame.mixer.quit()

    w = settings.display.canvas.width
    h = settings.display.canvas.height
    screen = pygame.display.set_mode((w, h), pygame.SRCALPHA)
    pygame.display.set_caption(f"wideboy v{__version__}")

    display = _create_display(settings, args.backend)
    display.start()

    state, entity_ids = _build_scene(settings)

    ha_service = _start_ha(settings, entity_ids)

    mqtt_service = None
    if settings.mqtt.enabled and settings.mqtt.host:
        from .services.mqtt_hass import MqttHassService

        mqtt_service = MqttHassService(settings.mqtt, state, settings)
        await mqtt_service.connect()

    stop_event = asyncio.Event()

    def _request_stop() -> None:
        if not stop_event.is_set():
            logger.info("Stop signal received, initiating shutdown")
            stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        with contextlib.suppress(NotImplementedError, RuntimeError, ValueError):
            loop.add_signal_handler(sig, _request_stop)

    main_task = asyncio.create_task(
        run_loop(
            screen,
            display,
            state,
            ha_service,
            mqtt_service,
            settings,
            args.test_pattern,
            stop_event,
        )
    )
    mqtt_task: asyncio.Task | None = None
    if mqtt_service:
        mqtt_task = asyncio.create_task(mqtt_service.run())

    try:
        await main_task
    finally:
        if mqtt_task is not None:
            mqtt_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await mqtt_task
        if mqtt_service:
            await mqtt_service.disconnect()
        if ha_service:
            ha_service.stop()
        with contextlib.suppress(Exception):
            display.stop()
        with contextlib.suppress(Exception):
            pygame.quit()
        logger.info("Shutdown complete")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
