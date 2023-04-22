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
from wideboy.homeassistant.mqtt import MQTTClient
from wideboy.config import settings


logger = logging.getLogger("homeassistant")


class HASSManager:
    def __init__(self, device_id: str):
        self.client = Client(
            f"{settings.homeassistant.url}/api",
            settings.homeassistant.api_token,
            cache_session=False,
        )
        self.mqtt = MQTTClient(device_id=device_id)
