from __future__ import annotations

import logging

import pygame

from .base import Display

logger = logging.getLogger(__name__)


class EmulatorDisplay(Display):
    def __init__(self, settings) -> None:
        self.settings = settings
        self.matrix = None
        self.buffer = None

    def start(self) -> None:
        try:
            from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
        except ImportError:
            logger.error(
                "RGBMatrixEmulator not installed. Install with: uv pip install RGBMatrixEmulator"
            )
            raise

        options = RGBMatrixOptions()
        options.rows = self.settings.display.canvas.height
        options.cols = self.settings.display.canvas.width
        options.chain_length = 1
        options.parallel = 1
        options.pixel_size = 8

        self.matrix = RGBMatrix(options=options)
        self.buffer = self.matrix.CreateFrameCanvas()
        logger.info("Emulator display started (%dx%d)", options.cols, options.rows)

    def present(self, surface: pygame.Surface) -> None:
        if self.matrix is None:
            return
        image = self.surface_to_pil(surface)
        self.buffer.SetImage(image)
        self.matrix.SwapOnVSync(self.buffer)

    def stop(self) -> None:
        if self.matrix is not None:
            self.matrix.Clear()
            logger.info("Emulator display stopped")
