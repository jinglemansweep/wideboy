import json
import logging
import pygame
from typing import Any, Optional
import paho.mqtt.client as mqtt

from wideboy.config import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD
from wideboy.utils.hass import on_mqtt_message

MQTT_PREFIX = "wideboy"
EVENT_MQTT_MESSAGE = pygame.USEREVENT + 21

logger = logging.getLogger(__name__)


def setup_mqtt():
    mqtt = MQTT(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD)
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
        self.client: mqtt.Client = mqtt.Client()
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

    def publish(
        self, topic: str, payload: dict, retain: bool = True, qos: int = 1
    ) -> mqtt.MQTTMessageInfo:
        json_payload = json.dumps(payload)
        logger.debug(
            f"mqtt:publish topic={topic} payload={json_payload} retain={retain} qos={qos}"
        )
        return self.client.publish(topic, json_payload, retain=retain, qos=qos)

    def subscribe(self, topic: str, args: Any) -> None:
        logger.debug(f"mqtt:subscribe topic={topic}")
        self.client.subscribe(topic, args)

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(
            f"mqtt:connect client={client} userdata={userdata} flags={flags} rc={str(rc)}"
        )

    def _on_message(self, client, userdata, msg):
        topic, payload = str(msg.topic), msg.payload.decode("utf-8")
        logger.debug(
            f"mqtt:message topic={topic} payload={payload} client={client} userdata={userdata}"
        )
        on_mqtt_message(topic, payload)
        # pygame.event.post(
        #     pygame.event.Event(EVENT_MQTT_MESSAGE, dict(topic=topic, payload=payload))
        # )
