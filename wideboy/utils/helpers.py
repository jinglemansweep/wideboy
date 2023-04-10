import logging
from datetime import datetime
from typing import Any
from wideboy.constants import AppMetadata
from wideboy.config import settings

logger = logging.getLogger("utils.helpers")


def intro_debug(device_id: str) -> None:
    logger.info("=" * 80)
    logger.info(
        f"{AppMetadata.DESCRIPTION} [{AppMetadata.NAME}] v{AppMetadata.VERSION}"
    )
    logger.info("=" * 80)
    logger.info(f"Device ID:   {device_id}")
    logger.info(f"Debug:       {settings.general.debug}")
    logger.info(f"Log Level:   {settings.general.log_level}")
    logger.info(
        f"Canvas Size: {settings.display.canvas.width}x{settings.display.canvas.height}"
    )
    logger.info("=" * 80)
