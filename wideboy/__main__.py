import os
import logging
import pygame
from dynaconf import Dynaconf
from ecs_pattern import EntityManager, SystemManager

from . import _APP_NAME, _APP_TITLE, _APP_VERSION
from .config import VALIDATORS
from .consts import FPS_MAX
from .entities import AppState
from .systems.animation import SysMovement
from .systems.boot import SysBoot, SysClock, SysDebug, SysEvents, SysInput
from .systems.display import SysDisplay
from .systems.draw import SysDraw
from .systems.scenes.default import SysScene
from .systems.scenes.default.hass_entities import ENTITIES as HASS_ENTITIES
from .systems.mqtt import SysMQTT, SysHomeAssistant
from .systems.preprocess import SysPreprocess
from .utils import setup_logger

os.environ["SDL_VIDEO_CENTERED"] = "1"


config = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)


def main():
    app_state = AppState(running=True, booting=True, config=config)

    setup_logger(config)
    logger = logging.getLogger(__name__)

    logger.info(f"{_APP_TITLE} v{_APP_VERSION} starting up...")

    pygame.init()
    pygame.mixer.quit()
    pygame.display.set_caption(f"{_APP_TITLE} v{_APP_VERSION}")
    clock = pygame.time.Clock()

    entities = EntityManager()
    entities.add(app_state)

    screen = pygame.display.set_mode(
        (app_state.config.display.canvas.width, app_state.config.display.canvas.height)
    )

    system_manager = SystemManager(
        [
            # Boot
            SysBoot(entities, config),
            SysPreprocess(entities),
            # Inputs/Control
            SysEvents(entities),
            SysClock(entities),
            SysInput(entities),
            SysMQTT(entities),
            SysHomeAssistant(entities, hass_entities=HASS_ENTITIES),
            # Stage
            SysScene(entities),
            SysMovement(entities),
            # Render
            SysDraw(entities, screen),
            SysDisplay(entities, screen),
            # Debugging
            SysDebug(entities),
        ]
    )
    system_manager.start_systems()

    while app_state.running:
        clock.tick(FPS_MAX)
        system_manager.update_systems()
        pygame.display.flip()

    system_manager.stop_systems()


if __name__ == "__main__":
    main()
