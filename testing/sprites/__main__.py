import datetime
import enum
import logging
import pygame
import random
import time
from typing import Dict, List, Tuple

from .tiles import CustomTileGrid

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Setup

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 64


# Main Loop

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)

clock = pygame.time.Clock()
FPS = 50
DEBUG = True


def randomise_state(state: Dict):
    state.update(
        dict(
            download=random.randint(0, 1000),
            upload=random.randint(0, 1000),
            ping=random.randint(0, 100),
            fan=random.randint(0, 100),
        )
    )


frame = 0
state: Dict = dict()
running = True


tile_grid = CustomTileGrid(state)

sprite_group: pygame.sprite.Group = pygame.sprite.Group()
sprite_group.add(tile_grid)

while running:
    now = datetime.datetime.now()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if frame % 100 == 0:
        randomise_state(state)
        print(f"State: {state}")

    screen.fill((0, 0, 0, 255))
    sprite_group.update()
    sprite_group.draw(screen)
    # tile_grid.rect.topright = (SCREEN_WIDTH, 0)
    pygame.display.flip()
    clock.tick(FPS)
    if frame % 100 == 0:
        logger.debug(f"Frame: {frame}, FPS: {clock.get_fps()}")
    frame += 1

pygame.quit()
