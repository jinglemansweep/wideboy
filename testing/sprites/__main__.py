import enum
import logging
import pygame

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
    BOTH = enum.auto()


class BaseSprite(pygame.sprite.Sprite):
    pass


class CellGroup(pygame.sprite.Group):
    def update(self):
        super().update()
        cy = 0
        for sprite in self.sprites():
            sprite.rect.y = cy
            cy += sprite.rect.height


class Cell(BaseSprite):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        width_closed: int = 2,
        height_closed: int = 2,
        open: bool = True,
        color: pygame.Color = pygame.Color(0, 0, 0),
        collapse_style: CellCollapseStyle = CellCollapseStyle.HORIZONTAL,
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
        self.open_state = CellStates.OPEN if open else CellStates.CLOSED
        self.collapse_style = collapse_style
        self.color = color
        self.debug = debug
        self.render(force_redraw=True)

    def update(self):
        if self.debug:
            logger.debug(f"Cell.update: {self.open_state}")
        self.handle_animation()
        self.render()

    def handle_animation(self):
        if self.open_state == CellStates.OPENING:
            if self.collapse_style in [
                CellCollapseStyle.VERTICAL,
                CellCollapseStyle.BOTH,
            ]:
                self.height += 1
                if self.height >= self.height_open:
                    self.height = self.height_open
            if self.collapse_style in [
                CellCollapseStyle.HORIZONTAL,
                CellCollapseStyle.BOTH,
            ]:
                self.width += 1
                if self.width >= self.width_open:
                    self.width = self.width_open
            if self.height == self.height_open and self.width == self.width_open:
                self.open_state = CellStates.OPEN
        elif self.open_state == CellStates.CLOSING:
            if self.collapse_style in [
                CellCollapseStyle.VERTICAL,
                CellCollapseStyle.BOTH,
            ]:
                self.height -= 1
                if self.height <= self.height_closed:
                    self.height = self.height_closed
            if self.collapse_style in [
                CellCollapseStyle.HORIZONTAL,
                CellCollapseStyle.BOTH,
            ]:
                self.width -= 1
                if self.width <= self.width_closed:
                    self.width = self.width_closed
            if self.height == self.height_closed and self.width == self.width_closed:
                self.open_state = CellStates.CLOSED

    def render(self, force_redraw: bool = False):
        if force_redraw or self.open_state in [CellStates.OPENING, CellStates.CLOSING]:
            self.redraw_image(self.width, self.height)
        self.draw_text()

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

    def redraw_image(self, width: int, height: int):
        self.image = pygame.Surface((width, height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def draw_text(self):
        text = render_text(
            "Hello World",
            font_filename=FONT_FILENAME,
            font_size=FONT_SIZE,
            color_fg=pygame.Color(255, 255, 255),
        )
        self.image.blit(text, (0, 0))


# Main Logic

clock = pygame.time.Clock()
FPS = 50

sprite_group: CellGroup = CellGroup()


sprite1 = Cell(0, 0, 100, 30, color=pygame.Color(128, 0, 0, 255))
sprite_group.add(sprite1)

sprite2 = Cell(0, 50, 100, 30, color=pygame.Color(0, 128, 0, 255))
sprite_group.add(sprite2)

sprite3 = Cell(0, 100, 100, 30, color=pygame.Color(0, 0, 128, 255))
sprite_group.add(sprite3)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                sprite1.toggle()
            elif event.key == pygame.K_2:
                sprite2.toggle()
            elif event.key == pygame.K_3:
                sprite3.toggle()

    screen.fill((0, 0, 0, 255))
    sprite_group.update()
    sprite_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
