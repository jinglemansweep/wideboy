import logging

LOG_FORMAT = "%(message)s"


def setup_logger(level: int = logging.INFO) -> None:
    log_level = logging.DEBUG if level == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
