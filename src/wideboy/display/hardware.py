from __future__ import annotations

import logging

import pygame

from .base import Display
from .remap import remap_logical_to_physical

logger = logging.getLogger(__name__)


class HardwareDisplay(Display):
    def __init__(self, settings) -> None:
        self.settings = settings
        self.matrix = None
        self.buffer = None

    def start(self) -> None:
        try:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions
        except ImportError:
            logger.error(
                "rpi-rgb-led-matrix not installed. "
                "Install on Pi with: uv pip install git+https://github.com/hzeller/rpi-rgb-led-matrix"
            )
            raise

        d = self.settings.display.matrix.driver
        options = RGBMatrixOptions()
        options.rows = d.rows
        options.cols = d.cols
        options.chain_length = d.chain
        options.parallel = d.parallel
        options.row_address_type = d.row_addr_type
        options.multiplexing = d.multiplexing
        if d.pixel_mapper:
            options.pixel_mapper_config = d.pixel_mapper
        options.pwm_bits = d.pwm_bits
        options.brightness = d.brightness
        options.scan_mode = d.scan_mode
        options.show_refresh_rate = int(d.show_refresh)
        options.led_rgb_sequence = d.rgb_sequence
        options.pwm_lsb_nanoseconds = d.pwm_lsb_nanoseconds
        options.pwm_dither_bits = d.pwm_dither_bits
        options.disable_hardware_pulsing = d.no_hardware_pulse
        if d.panel_type:
            options.panel_type = d.panel_type
        options.gpio_slowdown = d.slowdown_gpio
        options.daemon = int(d.daemon)
        options.drop_privileges = 0

        self.matrix = RGBMatrix(options=options)
        self.buffer = self.matrix.CreateFrameCanvas()
        logger.info(
            "Hardware display started (%dx%d, chain=%d, parallel=%d)",
            d.rows,
            d.cols,
            d.chain,
            d.parallel,
        )

    def present(self, surface: pygame.Surface) -> None:
        if self.matrix is None:
            return
        import numpy as np

        pixels = pygame.surfarray.pixels3d(surface)
        logical = np.transpose(pixels, (1, 0, 2))
        order = self.settings.display.matrix.remap.output_order
        physical = remap_logical_to_physical(logical, order)

        from PIL import Image

        image = Image.frombytes("RGB", (physical.shape[1], physical.shape[0]), physical.tobytes())
        self.buffer.SetImage(image)
        self.matrix.SwapOnVSync(self.buffer)

    def stop(self) -> None:
        if self.matrix is not None:
            self.matrix.Clear()
            logger.info("Hardware display stopped")
