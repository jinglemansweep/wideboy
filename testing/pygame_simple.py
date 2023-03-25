import numpy as np
import pygame
from pprint import pprint

pygame.init()
screen = pygame.display.set_mode((12, 1), pygame.RESIZABLE | pygame.SCALED)
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((128, 0, 0))
    screen.set_at((0, 0), (255, 0, 0))
    screen.set_at((4, 0), (0, 255, 0))
    screen.set_at((8, 0), (0, 0, 255))

    original = pygame.surfarray.pixels3d(screen)
    reshaped = np.reshape(original, (4, 3, -1), order="F")

    print("original", original.shape)
    print("reshaped", reshaped.shape)
    assert (original[0, 0] == reshaped[0, 0]).all()
    assert (original[4, 0] == reshaped[0, 1]).all()
    assert (original[8, 0] == reshaped[0, 2]).all()

    pygame.display.flip()
    clock.tick(1)

pygame.quit()
