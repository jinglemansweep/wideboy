import logging
import pygame
import pygame.pkgdata
import sys
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from wideboy.constants import (
    AppMetadata,
)
from wideboy.config import settings
from wideboy.utils.logger import setup_logger
from wideboy.utils.helpers import main_entrypoint

# from wideboy.scenes.credits import CreditsScene
from wideboy.scenes.default import DefaultScene

# from wideboy.scenes.night import NightScene
from wideboy.controller import Controller

# Logging
setup_logger(level=settings.general.log_level)
logger = logging.getLogger(AppMetadata.NAME)


def main():
    controller = Controller(scenes=[DefaultScene])

    controller.start()


# Entrypoint
if __name__ == "__main__":
    main_entrypoint(main)
