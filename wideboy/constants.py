import pygame


class AppMetadata:
    NAME = "wideboy"
    TITLE = "WideBoy"
    DESCRIPTION = "WideBoy RGB Matrix Platform"
    VERSION = "0.0.1"
    AUTHOR = "JingleManSweep"
    REPO_URL = "https://github.com/jinglemansweep/wideboy"


DYNACONF_ENVVAR_PREFIX = "WIDEBOY"

EVENT_MASTER_POWER = pygame.USEREVENT + 11
EVENT_MASTER_BRIGHTNESS = pygame.USEREVENT + 12
EVENT_SCENE_NEXT = pygame.USEREVENT + 21

EVENT_EPOCH_SECOND = pygame.USEREVENT + 31
EVENT_EPOCH_MINUTE = pygame.USEREVENT + 32
EVENT_EPOCH_HOUR = pygame.USEREVENT + 33

EVENT_MQTT_MESSAGE = pygame.USEREVENT + 41
EVENT_HASS_COMMAND = pygame.USEREVENT + 42
