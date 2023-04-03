import pygame
from enum import Enum


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
EVENT_NOTIFICATION_RECEIVED = pygame.USEREVENT + 22
EVENT_ACTION_A = pygame.USEREVENT + 23
EVENT_ACTION_B = pygame.USEREVENT + 24

EVENT_EPOCH_SECOND = pygame.USEREVENT + 51
EVENT_EPOCH_MINUTE = pygame.USEREVENT + 52
EVENT_EPOCH_HOUR = pygame.USEREVENT + 53

EVENT_MQTT_MESSAGE = pygame.USEREVENT + 61
EVENT_HASS_COMMAND = pygame.USEREVENT + 62

# GAMEPAD

# Stadia Controller
# 0: A, 1: B, 2: X, 3: Y, 4: LB, 5: RB, 6: LT, 7: RT, 8: Back, 9: Start, 10: L3, 11: R3, 12: Dpad Up, 13: Dpad Down, 14: Dpad Left, 15: Dpad Right


class GAMEPAD(Enum):
    BUTTON_A = 0
    BUTTON_B = 1
    BUTTON_X = 2
    BUTTON_Y = 3
    BUTTON_L = 4
    BUTTON_R = 5
