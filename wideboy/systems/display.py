import logging
import os
import sys
from dynaconf import Dynaconf
from ecs_pattern import EntityManager, System
from pygame import Color
from pygame.image import tostring as image_to_string
from pygame.surface import Surface
from PIL import Image
from typing import Any
from ..entities import AppState
from ..sprites.graphics import build_surface


logger = logging.getLogger(__name__)


def surface_to_led_matrix(surface: Surface) -> Image.Image:
    pixels = image_to_string(surface, "RGB")
    return Image.frombytes("RGB", (surface.get_width(), surface.get_height()), pixels)


class SysDisplay(System):
    entities: EntityManager
    screen: Surface
    screen_off: Surface
    config: Dynaconf
    enabled: bool

    def __init__(self, entities: EntityManager, screen: Surface) -> None:
        self.entities = entities
        self.screen = screen
        self.screen_off = build_surface(screen.get_size(), Color(0, 0, 0))
        self.config = next(self.entities.get_by_class(AppState)).config
        self.enabled = self.config.display.matrix.enabled

    def start(self) -> None:
        if not self.enabled:
            logger.info("Display system disabled")
            return
        logger.info("Display system starting...")
        self._setup_matrix_driver()

    def update(self) -> None:
        app_state = next(self.entities.get_by_class(AppState))
        if not self.enabled:
            return
        render_surface = self.screen if app_state.master_power else self.screen_off
        self.buffer.SetImage(surface_to_led_matrix(render_surface))
        self.matrix.SetBrightness((app_state.master_brightness / 255) * 100)
        self.matrix.SwapOnVSync(self.buffer)

    def _setup_matrix_driver(self) -> None:
        self._update_python_path()
        from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

        self.options = RGBMatrixOptions()
        self._set_matrix_options(self.options, self.config.display.matrix.driver)
        self.matrix = RGBMatrix(options=self.options)
        self.buffer = self.matrix.CreateFrameCanvas()

    def _set_matrix_options(self, options: Any, config: Dynaconf) -> None:
        options.rows = config.rows
        options.cols = config.cols
        options.chain_length = config.chain
        options.parallel = config.parallel
        options.row_address_type = config.row_addr_type
        options.multiplexing = config.multiplexing
        options.pixel_mapper_config = config.pixel_mapper
        options.pwm_bits = config.pwm_bits
        options.brightness = config.brightness
        options.scan_mode = config.scan_mode
        options.show_refresh_rate = config.show_refresh
        if config.limit_refresh:
            options.limit_refresh_rate_hz = config.limit_refresh
        # options.inverse = config.inverse
        options.led_rgb_sequence = config.rgb_sequence
        options.pwm_lsb_nanoseconds = config.pwm_lsb_nanoseconds
        options.pwm_dither_bits = config.pwm_dither_bits
        options.disable_hardware_pulsing = config.no_hardware_pulse
        if config.panel_type:
            options.panel_type = config.panel_type
        options.gpio_slowdown = config.slowdown_gpio
        options.daemon = config.daemon
        options.drop_privileges = 0

    def _update_python_path(self) -> None:
        sys.path.append(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "lib/rpi-rgb-led-matrix/bindings/python",
                ),
            ),
        )
