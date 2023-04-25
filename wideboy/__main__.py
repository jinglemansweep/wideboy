import cProfile
import logging
import pygame
import pygame.pkgdata
import sys
from dotenv import load_dotenv, find_dotenv
from typing import Callable

load_dotenv(find_dotenv())

from wideboy.constants import (
    AppMetadata,
)
from wideboy.config import settings
from wideboy.controller import Controller
from wideboy.scenes.credits import CreditsScene
from wideboy.scenes.default import DefaultScene
from wideboy.scenes.night import NightScene
from wideboy.utils.logger import setup_logger


# Logging
setup_logger(level=settings.general.log_level)
logger = logging.getLogger(AppMetadata.NAME)

# SCENES
SCENES = [DefaultScene, NightScene, CreditsScene]

# ENTITIES
ENTITIES = []


def main():
    controller = Controller(scenes=SCENES, entities=ENTITIES)
    controller.start()


# Entrypoint
if __name__ == "__main__":
    if settings.general.profiling in ["ncalls", "tottime"]:
        cProfile.run("main()", None, sort=settings.general.profiling)
    else:
        main()
