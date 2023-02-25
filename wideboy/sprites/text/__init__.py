import logging
import pygame
import random
from pygame import SRCALPHA
from wideboy.utils.pygame import EVENT_EPOCH_SECOND, EVENT_EPOCH_MINUTE
from wideboy.sprites import BaseSprite


logger = logging.getLogger(__name__)

# ['bitstreamverasansmono', 'bitstreamverasans', 'anonymousprominus', 'anonymouspro', 'bitstreamveraserif']

# ChatGPT Prompt: "Write 5 funny positive news stories. Each headline should be no more than 6 words. Each summary should be no more than 15 words"

DUMMY_CONTENT = [
    [
        "SHOULD HAVE GONE TO SPECSAVERS",
        "This is the first line of the paragraph to prove whether or",
        "not this is comfortably readable at a distance without pain",
    ],
    [
        "WORLD AGREES TO LIVE HAPPILY EVER AFTER",
        "In some bizarre twist of fate, the citizens of the world",
        "have decided to be happy and get along",
    ],
    [
        "CHATGPT ATE MY HAMSTER",
        "Crazy new AI language model has become sentient and has",
        "acquired a taste for small rodents from the desert",
    ],
    [
        "KEBAB SHOP RUNS OUT OF CHICKEN",
        "Global shortages in social workers has caused mass",
        "depression in poultry who no longer want to be eaten",
    ],
    [
        "LOST WALLET RETURNED WITH EXTRA CASH",
        "A man's lost wallet was returned to him with extra cash",
        "inside, leaving him pleasantly surprised and grateful",
    ],
    [
        "GOAT ELECTED MAYOR OF TOWN",
        "A small town elected a goat as their honorary mayor,",
        "bringing humor and charm to local politics",
    ],
    [
        "MAN BUYS COW, GETS SURPRISE DONKEY",
        "A man who bought a cow online received a surprise donkey in",
        "the same shipment, leading to unexpected animal antics",
    ],
    [
        "CHILD'S DRAWING SELLS FOR MILLIONS",
        "A child's whimsical drawing sold for millions at an art auction,",
        "proving that creativity and imagination know no bounds",
    ],
    [
        "TOWN BUILD WORLD'S LARGEST SANDWICH!",
        "A town came together to build the world's largest sandwich,",
        "breaking a world record and having a delicious time",
    ],
]


def render_text(
    text: str,
    font: str,
    font_size: int,
    color_fg: pygame.color.Color,
    color_outline: pygame.color.Color = (0, 0, 0, 255),
    antialias: bool = True,
) -> pygame.surface.Surface:
    font = pygame.font.SysFont(font, font_size)
    surface_orig = font.render(text, antialias, color_fg)
    surface_dest = pygame.Surface(
        (surface_orig.get_rect().width + 2, surface_orig.get_rect().height + 2),
        SRCALPHA,
    )
    for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        surface_outline = font.render(text, antialias, color_outline)
        surface_dest.blit(surface_outline, (offset[0] + 1, offset[1] + 1))
    surface_dest.blit(surface_orig, (1, 1))
    return surface_dest


class TextSprite(BaseSprite):
    def __init__(
        self,
        rect: pygame.rect.Rect,
        heading_font: str = "bitstreamverasans",
        heading_font_size: int = 20,
        paragraph_font: str = "bitstreamverasans",
        paragraph_font_size: int = 16,
        color_bg: pygame.color.Color = (0, 0, 0, 128),
        color_fg: pygame.color.Color = (255, 255, 255, 255),
        color_outline: pygame.color.Color = (0, 0, 0, 255),
    ) -> None:
        super().__init__(rect)
        self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA)
        self.heading_font = heading_font
        self.heading_font_size = heading_font_size
        self.paragraph_font = paragraph_font
        self.paragraph_font_size = paragraph_font_size
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_outline = color_outline
        self.text_heading = None
        self.text_p1 = None
        self.text_p2 = None
        self.set_random_content()
        self.render()

    def update(
        self, frame: str, delta: float, events: list[pygame.event.Event]
    ) -> None:
        super().update(frame, delta, events)
        for event in events:
            if event.type == EVENT_EPOCH_SECOND:
                self.render()

    def render(self) -> None:
        self.image.fill(self.color_bg)
        heading_bg = pygame.surface.Surface((self.rect.width, 21))
        heading_bg.fill((0, 0, 0, 255))
        self.image.blit(heading_bg, (0, 0))
        heading_surface = render_text(
            self.text_heading,
            self.heading_font,
            self.heading_font_size,
            self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(heading_surface, (4, -2))
        para1_surface = render_text(
            self.text_p1,
            self.paragraph_font,
            self.paragraph_font_size,
            self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(para1_surface, (4, 20))
        para2_surface = render_text(
            self.text_p2,
            self.paragraph_font,
            self.paragraph_font_size,
            self.color_fg,
            color_outline=self.color_outline,
        )
        self.image.blit(para2_surface, (4, 36))
        self.dirty = 1

    def set_random_content(self) -> None:
        heading, p1, p2 = random.choice(DUMMY_CONTENT)
        self.text_heading = heading
        self.text_p1 = p1
        self.text_p2 = p2
