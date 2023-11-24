import pygame


class GroupThing(pygame.sprite.Group):
    def __init__(self, *sprites, groups=None):
        super().__init__(*sprites)
        self.groups = groups or []

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        for group in self.groups:
            group.update(*args, **kwargs)

    def draw(self, surface):
        super().draw(surface)
        for group in self.groups:
            group.draw(surface)
