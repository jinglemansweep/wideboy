import enum
import logging
import pygame
import random
import time
from typing import Tuple

from .utils import render_text


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 64

# Sprites

FONT_FILENAME = "fonts/bitstream-vera.ttf"
FONT_SIZE = 12


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


class CellRow(BaseSprite):
    def __init__(self, x: int, y: int, width: int, height: int, cells: [BaseSprite]):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cells = cells
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.render()

    def update(self):
        self.render()

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        cx = 0
        for cell in self.cells:
            cell.update()
            cell.render()
            surface.blit(cell.image, (cx, 0))
            cx += cell.rect.width
        print(([cell.evaluate() for cell in self.cells]))
        self.image = pygame.Surface((cx, self.height))
        self.image.blit(surface, (0, 0))
        self.rect = self.image.get_rect()


class CellColumn(BaseSprite):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        cells: [BaseSprite],
        border_width: int = 1,
        border_color: pygame.Color = pygame.Color(255, 255, 255),
        border_padding: int = 0,
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cells = cells
        self.border_width = border_width
        self.border_color = border_color
        self.border_padding = border_padding
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.render()

    def update(self):
        self.render()

    def render(self):
        surface = pygame.Surface((self.width, self.height))
        surface.fill(
            self.border_color, pygame.Rect(0, 0, self.border_width, self.height)
        )
        cx, cy = self.border_width + self.border_padding, 0
        for cell in self.cells:
            cell.update()
            cell.render()
            surface.blit(cell.image, (cx, cy))
            cy += cell.rect.height if cell.rect.height > 1 else 0
        self.image.blit(surface, (0, 0))
        self.rect = self.image.get_rect()

    def evaluate(self):
        test = lambda cell: cell.open_state == CellStates.OPEN
        logger.debug(f"CellColumn.evaluate: {[test(cell) for cell in self.cells]}")
        return any([test(cell) for cell in self.cells])


class Cell(BaseSprite):
    def __init__(
        self,
        width: int,
        height: int,
        text: str,
        font: str = FONT_FILENAME,
        size: int = FONT_SIZE,
        color_fg=pygame.Color(255, 255, 255),
        color_bg=pygame.Color(0, 0, 0, 0),
        color_outline=None,
        padding: Tuple[int, int] = (0, -2),
        seed: int = 30,
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
        self.padding = padding
        self.seed = seed
        self.render()

    def render(self):
        self.image = pygame.Surface(
            (self.width, self.height),
        )
        self.image.fill(self.color_bg)
        text_surface = render_text(
            self.text,
            font_filename=self.font,
            font_size=self.size,
            color_fg=self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(text_surface, (3 + self.padding[0], 0 + self.padding[1]))

    def evaluate(self):
        x = int(time.time() % 60)
        return 0 < x < self.seed


class Collapsible(BaseSprite):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        sprite: BaseSprite,
        width_closed: int = 0,
        height_closed: int = 0,
        open: bool = True,
        collapse_style: CellCollapseStyle = CellCollapseStyle.HORIZONTAL,
        speed: int = 1,
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
        self.speed = speed
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
                self.height += self.speed
                if self.height >= self.height_open:
                    self.height = self.height_open
                if self.height == self.height_open:
                    self.open_state = CellStates.OPEN
            # Open Horizontal
            if self.collapse_style == CellCollapseStyle.HORIZONTAL:
                self.width += self.speed
                if self.width >= self.width_open:
                    self.width = self.width_open
                if self.width == self.width_open:
                    self.open_state = CellStates.OPEN
        elif self.open_state == CellStates.CLOSING:
            # Close Vertical
            if self.collapse_style == CellCollapseStyle.VERTICAL:
                self.height -= self.speed
                if self.height <= self.height_closed:
                    self.height = self.height_closed
                if self.height == self.height_closed:
                    self.open_state = CellStates.CLOSED
            # Close Horizontal
            if self.collapse_style == CellCollapseStyle.HORIZONTAL:
                self.width -= self.speed
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
            self.sprite.update()
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


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)


clock = pygame.time.Clock()
FPS = 50
DEBUG = True

cell_group: CellGroup = CellGroup()

CELL_WIDTH = 64
CELL_HEIGHT = 12

COLUMN_COUNT = 4

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
    content = Cell(CELL_WIDTH, CELL_HEIGHT, f"Item {i}", seed=(i * 10) % 60)
    contents.append(content)


sprites = []
for i in range(1, 20):
    sprite = Collapsible(
        0 * CELL_WIDTH,
        0,
        CELL_WIDTH,
        CELL_HEIGHT,
        contents[i % len(contents)],
        collapse_style=CellCollapseStyle.VERTICAL,
        debug=DEBUG,
    )
    sprites.append(sprite)

columns = []

for i in range(COLUMN_COUNT):
    shuffled_sprites = sprites.copy()
    random.shuffle(shuffled_sprites)
    column_sprites = shuffled_sprites[:5]
    cell_column = CellColumn(
        0,
        0,
        CELL_WIDTH,
        SCREEN_HEIGHT,
        column_sprites,
        border_color=colors[i % COLUMN_COUNT],
    )
    collapsible = Collapsible(
        0,
        0,
        CELL_WIDTH,
        CELL_HEIGHT * len(column_sprites),
        cell_column,
        collapse_style=CellCollapseStyle.HORIZONTAL,
        width_closed=3,
        debug=DEBUG,
    )
    columns.append(collapsible)

row = CellRow(0, 0, CELL_WIDTH * len(columns), SCREEN_HEIGHT, columns)

cell_group.add(row)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # if event.type == pygame.KEYDOWN:
        #    if pygame.K_1 <= event.key <= pygame.K_8:
        #        numkey = event.key - pygame.K_0 - 1
        #        sprites[numkey].toggle()

    screen.fill((0, 0, 0, 255))
    cell_group.update()
    cell_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
