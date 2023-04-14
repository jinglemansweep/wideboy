import logging

LOG_FORMAT = "%(name)-20s %(levelname)-7s %(message)s"

logging.getLogger("homeassistant_api").setLevel(logging.WARNING)
logging.getLogger("requests_cache").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)


def setup_logger(level: int = logging.INFO) -> None:
    log_level = logging.DEBUG if level == "debug" else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
