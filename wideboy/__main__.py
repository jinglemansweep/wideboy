import os

import pygame
from dynaconf import Dynaconf
from ecs_pattern import EntityManager, SystemManager

from . import _APP_NAME, _APP_TITLE, _APP_VERSION
from .config import VALIDATORS
from .consts import FPS_MAX
from .entities import AppState
from .systems.animation import SysMovement
from .systems.boot import SysBoot, SysClock, SysDebug, SysInput
from .systems.display import SysDraw
from .systems.scene import SysScene
from .systems.mqtt import SysMQTT, SysHomeAssistant


os.environ["SDL_VIDEO_CENTERED"] = "1"


config = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)


def main():
    pygame.init()
    pygame.display.set_caption(f"{_APP_TITLE} v{_APP_VERSION}")
    clock = pygame.time.Clock()

    app_state = AppState(running=True, config=config)

    entities = EntityManager()
    entities.add(app_state)

    screen = pygame.display.set_mode(
        (app_state.config.display.canvas.width, app_state.config.display.canvas.height)
    )

    system_manager = SystemManager(
        [
            # Boot
            SysBoot(entities, config),
            # Inputs/Control
            SysClock(entities),
            SysInput(entities),
            SysMQTT(entities),
            SysHomeAssistant(entities),
            # Stage
            SysScene(entities),
            SysMovement(entities),
            # Render
            SysDraw(entities, screen),
            # Debugging
            SysDebug(entities),
        ]
    )
    system_manager.start_systems()

    while app_state.running:
        clock.tick_busy_loop(FPS_MAX)
        system_manager.update_systems()
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()


if __name__ == "__main__":
    main()
