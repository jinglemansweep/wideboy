import logging
import pygame
from typing import Optional
import paho.mqtt.client as mqtt

from wideboy.config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
from wideboy.utils.hass import setup_hass_entities

MQTT_PREFIX = "wideboy"
EVENT_MQTT_MESSAGE = pygame.USEREVENT + 21

logger = logging.getLogger(__name__)


def setup_mqtt():
    mqtt = MQTT(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
    setup_hass_entities(mqtt.client)
    return mqtt


class MQTT:
    def __init__(
        self,
        host: str,
        port: int,
        user: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: Optional[int] = 60,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connect()

    def connect(self) -> None:
        logger.debug(
            f"mqtt:connecting host={self.host} port={self.port} user={self.user} password={self.password or '***'}"
        )
        if self.user is not None:
            self.client.username_pw_set(self.user, self.password)
        self.client.connect(self.host, self.port, self.keepalive)

    def loop(self, timeout: float = 0.1) -> None:
        self.client.loop(timeout)

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(
            f"mqtt:connect client={client} userdata={userdata} flags={flags} rc={str(rc)}"
        )
        self.client.subscribe(f"{MQTT_PREFIX}/#")

    def _on_message(self, client, userdata, msg):
        topic, payload = msg.topic, msg.payload.decode("utf-8")
        logger.debug(f"mqtt:message topic={topic} payload={payload}")
        pygame.event.post(
            pygame.event.Event(EVENT_MQTT_MESSAGE, dict(topic=topic, payload=payload))
        )
