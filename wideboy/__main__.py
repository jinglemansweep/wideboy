import os

import pygame
from dynaconf import Dynaconf
from ecs_pattern import EntityManager, SystemManager

from .config import VALIDATORS
from .consts import FPS_MAX
from .entities import AppState
from .systems.animation import SysMovement
from .systems.boot import SysBoot, SysClock, SysDebug, SysInput
from .systems.display import SysDraw
from .systems.scene import SysScene
from .systems.mqtt import SysMQTT, SysHomeAssistant


os.environ["SDL_VIDEO_CENTERED"] = "1"  # window at center


config = Dynaconf(
    envvar_prefix="WIDEBOY",
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)


def main():
    pygame.init()  # init all imported pygame modules

    pygame.display.set_caption("Main")
    screen = pygame.display.set_mode((800, 500))  # w h

    clock = pygame.time.Clock()

    entities = EntityManager()

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

    app_state = next(entities.get_by_class(AppState))

    while app_state.running:
        clock.tick_busy_loop(FPS_MAX)
        system_manager.update_systems()
        pygame.display.flip()  # draw changes on screen

    system_manager.stop_systems()


if __name__ == "__main__":
    main()
