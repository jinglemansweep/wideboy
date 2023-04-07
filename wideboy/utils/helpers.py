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


class EpochEmitter:
    def __init__(self) -> None:
        self._update()

    def check(self, unit=None) -> Any:
        now = datetime.timetuple(datetime.now())
        is_new_sec = now.tm_sec != self.then.tm_sec
        is_new_min = now.tm_min != self.then.tm_min
        is_new_hour = now.tm_hour != self.then.tm_hour
        is_new_mday = now.tm_mday != self.then.tm_mday
        epochs = dict(
            sec=now.tm_sec,
            min=now.tm_min,
            hour=now.tm_hour,
            mday=now.tm_mday,
            new_sec=is_new_sec,
            new_min=is_new_min,
            new_hour=is_new_hour,
            new_mday=is_new_mday,
        )
        self._update()
        if unit is not None:
            return epochs.get(unit)
        else:
            return epochs

    def _update(self) -> None:
        self.then = datetime.timetuple(datetime.now())
