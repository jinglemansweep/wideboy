import json
import logging
import pygame
from dynaconf import Dynaconf
from pygame import Event
from typing import Optional
from homeassistant_api import Client

from wideboy.constants import (
    AppMetadata,
    EVENT_MQTT_MESSAGE_SEND,
)
from wideboy.config import settings


logger = logging.getLogger("homeassistant")


class HASSManager:
    def __init__(self, options: Dynaconf):
        self.options = options
