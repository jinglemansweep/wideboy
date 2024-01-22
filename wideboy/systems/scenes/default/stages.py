import logging
import random
from typing import Tuple
from ..utils import Stage
from ....entities import WidgetImage
from ....sprites.image import build_image_sprite

logger = logging.getLogger(__name__)

IMAGE_DUCK = "images/icons/emoji-duck.png"
IMAGE_CAT = "images/icons/emoji-cat.png"


class StageDefault(Stage):
    image_count: int

    def __init__(self, display_size: Tuple[int, int], image_count: int = 20) -> None:
        self.display_size = display_size
        self.image_count = image_count
        self.entities = []
        self.setup()

    def setup(self) -> None:
        images = [IMAGE_DUCK, IMAGE_CAT]
        for i in range(self.image_count):
            self.entities.append(
                WidgetImage(
                    build_image_sprite(
                        random.choice(images), random.randrange(64, 256)
                    ),
                    x=random.randint(0, self.display_size[0] - 32),
                    y=random.randint(0, self.display_size[1] - 32),
                    speed_x=random.choice([-2, -1, 1, 2]),
                    speed_y=random.choice([-2, -1, 1, 2]),
                ),  # type: ignore[call-arg]
            )

    def update(self) -> None:
        pass
        # logger.debug(f"stage.default.update: entities={len(self.entities)}")


class StageNight(Stage):
    image_count: int

    def __init__(self, display_size: Tuple[int, int], image_count: int = 5) -> None:
        self.display_size = display_size
        self.image_count = image_count
        self.entities = []
        self.setup()

    def setup(self) -> None:
        for i in range(self.image_count):
            self.entities.append(
                WidgetImage(
                    build_image_sprite(IMAGE_DUCK, random.randrange(32, 128)),
                    x=random.randint(0, self.display_size[0] - 32),
                    y=random.randint(0, self.display_size[1] - 32),
                    speed_x=random.choice([-1, 0, 1]),
                    speed_y=random.choice([-1, 0, 1]),
                ),  # type: ignore[call-arg]
            )

    def update(self) -> None:
        pass
        # logger.debug(f"stage.night.update: entities={len(self.entities)}")
