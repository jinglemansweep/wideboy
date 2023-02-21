import logging

LOG_FORMAT = "%(message)s"


def setup_logger(debug: bool = False) -> None:

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO, format=LOG_FORMAT
    )
