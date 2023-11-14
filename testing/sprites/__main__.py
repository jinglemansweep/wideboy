import enum
import logging
import pygame
import random
import time

from .utils import render_text

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


pygame.init()
screen = pygame.display.set_mode((800, 600))

# Sprites

FONT_FILENAME = "fonts/bitstream-vera.ttf"
FONT_SIZE = 20


class CellStates(enum.Enum):
    OPEN = enum.auto()
    CLOSED = enum.auto()
    OPENING = enum.auto()
    CLOSING = enum.auto()


class CellCollapseStyle(enum.Enum):
    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()


class BaseSprite(pygame.sprite.Sprite):
    pass


class CellGroup(pygame.sprite.Group):
    def update(self):
        super().update()
        cy = 0
        for sprite in self.sprites():
            sprite.rect.y = cy
            cy += sprite.rect.height


class CellContent(BaseSprite):
    def __init__(
        self,
        width: int,
        height: int,
        text: str,
        font=FONT_FILENAME,
        size: int = FONT_SIZE,
        color_fg=pygame.Color(255, 255, 255),
        color_bg=pygame.Color(0, 0, 0, 0),
        color_outline=None,
        seed: int = 5,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.size = size
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.color_outline = color_outline
        self.seed = seed
        self.render()

    def render(self):
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color_bg)
        text_surface = render_text(
            self.text,
            font_filename=self.font,
            font_size=self.size,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(text_surface, (0, 0))

    def evaluate(self):
        current_second = time.localtime().tm_sec
        return current_second % self.seed == 0


class Cell(BaseSprite):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        sprite: BaseSprite,
        width_closed: int = 2,
        height_closed: int = 2,
        open: bool = True,
        collapse_style: CellCollapseStyle = CellCollapseStyle.HORIZONTAL,
        color_bg: pygame.Color = pygame.Color(0, 0, 0, 0),
        debug: bool = False,
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.width_open = width
        self.width_closed = width_closed
        self.width = self.width_open if open else self.width_closed
        self.height_open = height
        self.height_closed = height_closed
        self.height = self.height_open if open else self.height_closed
        self.sprite = sprite
        self.open_state = CellStates.OPEN if open else CellStates.CLOSED
        self.collapse_style = collapse_style
        self.color_bg = color_bg
        self.debug = debug
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()

    def update(self):
        if self.debug:
            logger.debug(f"Cell.update: {self.open_state}")
        if self.open_state in [CellStates.OPEN, CellStates.CLOSED]:
            self.open_state = (
                CellStates.OPENING if self.evaluate() else CellStates.CLOSING
            )
        self.handle_animation()
        self.render()

    def handle_animation(self):
        if self.open_state == CellStates.OPENING:
            # Open Vertical
            if self.collapse_style == CellCollapseStyle.VERTICAL:
                self.height += 1
                if self.height >= self.height_open:
                    self.height = self.height_open
                if self.height == self.height_open:
                    self.open_state = CellStates.OPEN
            # Open Horizontal
            if self.collapse_style == CellCollapseStyle.HORIZONTAL:
                self.width += 1
                if self.width >= self.width_open:
                    self.width = self.width_open
                if self.width == self.width_open:
                    self.open_state = CellStates.OPEN
        elif self.open_state == CellStates.CLOSING:
            # Close Vertical
            if self.collapse_style == CellCollapseStyle.VERTICAL:
                self.height -= 1
                if self.height <= self.height_closed:
                    self.height = self.height_closed
                if self.height == self.height_closed:
                    self.open_state = CellStates.CLOSED
            # Close Horizontal
            if self.collapse_style == CellCollapseStyle.HORIZONTAL:
                self.width -= 1
                if self.width <= self.width_closed:
                    self.width = self.width_closed
                if self.width == self.width_closed:
                    self.open_state = CellStates.CLOSED

    def render(self, force_redraw: bool = False):
        if force_redraw or self.open_state in [CellStates.OPENING, CellStates.CLOSING]:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color_bg)
            self.rect = self.image.get_rect()
        if self.sprite.image is not None and self.image is not None:
            self.image.blit(self.sprite.image, (0, 0))
            self.rect = self.image.get_rect()

    def toggle(self):
        if self.open_state == CellStates.OPEN or self.open_state == CellStates.OPENING:
            self.open_state = CellStates.CLOSING
        elif (
            self.open_state == CellStates.CLOSED
            or self.open_state == CellStates.CLOSING
        ):
            self.open_state = CellStates.OPENING
        if self.debug:
            logger.debug(f"Cell.toggle: {self.open_state}")

    def evaluate(self):
        return self.sprite.evaluate()


# Main Logic

clock = pygame.time.Clock()
FPS = 50
DEBUG = False

cell_group: CellGroup = CellGroup()

CELL_WIDTH = 100
CELL_HEIGHT = 50

content_r = CellContent(
    CELL_WIDTH,
    CELL_HEIGHT,
    "RED",
    color_bg=pygame.Color(128, 0, 0, 255),
    seed=random.randint(5, 10),
)
content_g = CellContent(
    CELL_WIDTH,
    CELL_HEIGHT,
    "GREEN",
    color_bg=pygame.Color(0, 128, 0, 255),
    seed=random.randint(5, 10),
)
content_b = CellContent(
    CELL_WIDTH,
    CELL_HEIGHT,
    "BLUE",
    color_bg=pygame.Color(0, 0, 128, 255),
    seed=random.randint(5, 10),
)

colors = [
    pygame.Color(128, 0, 0, 255),
    pygame.Color(0, 128, 0, 255),
    pygame.Color(0, 0, 128, 255),
    pygame.Color(128, 128, 0, 255),
    pygame.Color(128, 0, 128, 255),
    pygame.Color(0, 128, 128, 255),
    pygame.Color(128, 128, 128, 255),
]

contents = []

for i in range(9):
    content = CellContent(
        CELL_WIDTH,
        CELL_HEIGHT,
        f"Content {i}",
        color_bg=random.choice(colors),
        seed=random.randint(5, 10),
    )
    contents.append(content)


sprites = []

for i in range(9):
    sprite = Cell(
        0 * CELL_WIDTH,
        0,
        CELL_WIDTH,
        CELL_HEIGHT,
        contents[i % len(contents)],
        collapse_style=CellCollapseStyle.VERTICAL,
        debug=DEBUG,
    )
    sprites.append(sprite)

for sprite in sprites:
    cell_group.add(sprite)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if pygame.K_0 <= event.key <= pygame.K_9:
                numkey = event.key - pygame.K_0
                sprites[numkey].toggle()

    screen.fill((0, 0, 0, 255))
    cell_group.update()
    cell_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
