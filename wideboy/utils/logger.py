import logging

LOG_FORMAT = "%(name)-20s %(levelname)-7s %(message)s"


def setup_logger(level: int = logging.INFO) -> None:
    log_level = logging.DEBUG if level == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
