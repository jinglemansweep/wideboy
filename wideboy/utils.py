import logging
from dynaconf import Dynaconf

LOG_FORMAT = "%(name)-25s %(levelname)-7s %(message)s"

LOG_LEVELS = {
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def setup_logger(config: Dynaconf) -> None:
    logging.basicConfig(
        level=LOG_LEVELS.get(config.general.log_level, logging.INFO), format=LOG_FORMAT
    )
