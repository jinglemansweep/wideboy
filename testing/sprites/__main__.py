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


class BaseSprite(pygame.sprite.Sprite):
    pass


class Cell(BaseSprite):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        height_closed: int = 2,
        open: bool = True,
        color: pygame.Color = pygame.Color(0, 0, 0),
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height_open = height
        self.height_closed = height_closed
        self.height = self.height_open if open else self.height_closed
        self.open_state = CellStates.OPEN if open else CellStates.CLOSED
        self.color = color
        self.render(force_redraw=True)

    def update(self):
        logger.debug(f"Cell.update: {self.open_state}")
        self.handle_animation()
        self.render()

    def handle_animation(self):
        if self.open_state == CellStates.OPENING:
            self.height += 1
            if self.height >= self.height_open:
                self.height = self.height_open
                self.open_state = CellStates.OPEN
            logger.debug(f"Cell.handle_animation: OPENING {self.rect.height}")
        elif self.open_state == CellStates.CLOSING:
            self.height -= 1
            if self.height <= self.height_closed:
                self.height = self.height_closed
                self.open_state = CellStates.CLOSED
            logger.debug(f"Cell.handle_animation: CLOSING {self.rect.height}")

    def render(self, force_redraw: bool = False):
        if force_redraw or self.open_state in [CellStates.OPENING, CellStates.CLOSING]:
            self.redraw_image(self.width, self.height)
        self.draw_text()

    def toggle(self):
        if self.open_state == CellStates.OPEN:
            self.open_state = CellStates.CLOSING
        elif self.open_state == CellStates.CLOSED:
            self.open_state = CellStates.OPENING
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

sprite_group: pygame.sprite.Group = pygame.sprite.Group()


sprite1 = Cell(0, 0, 100, 50, color=pygame.Color(32, 0, 0, 255))
sprite_group.add(sprite1)

sprite2 = Cell(100, 0, 100, 50, color=pygame.Color(0, 32, 0, 255))
sprite_group.add(sprite2)

sprite3 = Cell(200, 0, 100, 50, color=pygame.Color(0, 0, 32, 255))
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
