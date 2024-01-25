import logging
from pygame import Rect, Surface, SRCALPHA
from pygame.sprite import Sprite
from pygame.transform import rotozoom, smoothscale


logger = logging.getLogger(__name__)


class Mode7Sprite(Sprite):
    image_original: Surface
    rect: Rect
    _perspective: float
    _rotation: float
    _zoom: float
    _dirty: bool

    def __init__(
        self,
        surface: Surface,
        perspective: float = 0,
        rotation: float = 0,
        zoom: float = 0,
    ) -> None:
        self.image_original = surface
        self.rect = surface.get_rect()
        self._perspective = perspective
        self._rotation = rotation
        self._zoom = zoom
        self._dirty = True

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        if value > 0:
            if not value == self._zoom:
                self._dirty = 1
                self._zoom = value
        else:
            raise ValueError

    @property
    def perspective(self):
        return self._perspective

    @perspective.setter
    def perspective(self, value):
        if 1 > value > 0:
            if not value == self._perspective:
                self._dirty = 1
                self._perspective = value
        else:
            raise ValueError

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if not value == self._rotation:
            self._dirty = 1
            self._rotation = value % 360

    @property
    def size(self):
        return self.image_original.get_size()

    def update(self):
        if not self._dirty:
            return
        surface = Surface((256, 64), SRCALPHA)
        surface.fill((0, 0, 0, 0))
        image = rotozoom(self.image_original, self._rotation, self._zoom)
        w2, h2 = image.get_size()
        image = smoothscale(image, (w2, int(h2 * self._perspective)))
        rect = image.get_rect()
        rect.center = surface.get_rect().center
        surface.blit(image, rect)
        self.image = surface
