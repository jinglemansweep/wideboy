import logging
import toml
import yaml
from dynaconf import Dynaconf
from typing import Any, Dict

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


def read_version_from_pyproject(file_path: str = "pyproject.toml"):
    try:
        pyproject_data = toml.load(file_path)
        return pyproject_data["tool"]["poetry"]["version"]
    except KeyError:
        return "Version information not found."


def read_yaml(file_path: str) -> Dict[str, Any]:
    """Read a YAML file and return its contents."""
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        if not isinstance(data, dict):
            raise ValueError("YAML content must be a dictionary")
        return data
