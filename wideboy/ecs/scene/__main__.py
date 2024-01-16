import os

import pygame
from ecs_pattern import EntityManager, SystemManager

from .consts import FPS_MAX
from .entities import AppState
from .systems import (
    SysClock,
    SysDraw,
    SysEventBus,
    SysInit,
    SysInputControl,
    SysMovement,
    SysMqttControl,
)

os.environ["SDL_VIDEO_CENTERED"] = "1"  # window at center


def main():
    pygame.init()  # init all imported pygame modules

    pygame.display.set_caption("Main")
    screen = pygame.display.set_mode((800, 500))  # w h

    clock = pygame.time.Clock()

    entities = EntityManager()

    system_manager = SystemManager(
        [
            SysInit(entities),
            SysClock(entities),
            SysMqttControl(entities),
            SysInputControl(entities, pygame.event.get),
            SysEventBus(entities),
            SysMovement(entities),
            SysDraw(entities, screen),
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
