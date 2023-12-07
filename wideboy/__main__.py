import cProfile
import logging
from dotenv import load_dotenv, find_dotenv
from typing import Type, List
from wideboy.constants import (
    AppMetadata,
)
from wideboy.config import settings
from wideboy.controller import Controller
from wideboy.homeassistant.hass import HASSEntity
from wideboy.scenes.base import BaseScene
from wideboy.scenes.credits import CreditsScene
from wideboy.scenes.default import DefaultScene
from wideboy.scenes.starfield import StarfieldScene
from wideboy.utils.logger import setup_logger

load_dotenv(find_dotenv())

# Logging
setup_logger(level=settings.general.log_level)
logger = logging.getLogger(AppMetadata.NAME)

# SCENES
SCENES: List[Type[BaseScene]] = [DefaultScene, StarfieldScene, CreditsScene]

# ENTITIES
ENTITIES: List[Type[HASSEntity]] = []


def main():
    controller = Controller(scenes=SCENES, entities=ENTITIES)
    controller.start()


# Entrypoint
if __name__ == "__main__":
    if settings.general.profiling in ["ncalls", "tottime"]:
        cProfile.run("main()", None, sort=settings.general.profiling)
    else:
        main()
