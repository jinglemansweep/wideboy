import json
import logging
import pygame
from typing import Any, Optional
import paho.mqtt.client as mqtt

from wideboy.config import (
    settings,
)
from wideboy.state import DEVICE_ID


EVENT_MQTT_MESSAGE = pygame.USEREVENT + 21
MQTT_TOPIC_PREFIX = settings.mqtt.topic_prefix

logger = logging.getLogger(__name__)


def setup_mqtt():
    mqtt = MQTTClient(
        settings.mqtt.host,
        settings.mqtt.port,
        settings.mqtt.user,
        settings.mqtt.password,
    )
    return mqtt


class MQTTClient:
    def __init__(
        self,
        host: str,
        port: int,
        user: Optional[str] = None,
        password: Optional[str] = None,
        keepalive: int = 60,
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
        self,
        topic: str,
        payload: dict,
        retain: bool = True,
        qos: int = 1,
        auto_prefix=True,
    ) -> mqtt.MQTTMessageInfo:
        json_payload = json.dumps(payload)
        topic_full = (
            f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/{topic}" if auto_prefix else topic
        )
        logger.debug(
            f"mqtt:publish topic={topic_full} payload={json_payload} retain={retain} qos={qos}"
        )
        return self.client.publish(topic_full, json_payload, retain=retain, qos=qos)

    def subscribe(self, topic: str, args: Any) -> None:
        logger.debug(f"mqtt:subscribe topic={topic}")
        self.client.subscribe(topic, args)

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(
            f"mqtt:connect client={client} userdata={userdata} flags={flags} rc={str(rc)}"
        )
        self.subscribe(f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/#", 1)

    def _on_message(self, client, userdata, msg):
        topic, payload = str(msg.topic), msg.payload.decode("utf-8")
        logger.debug(
            f"mqtt:message topic={topic} payload={payload} userdata={userdata}"
        )
        pygame.event.post(
            pygame.event.Event(EVENT_MQTT_MESSAGE, dict(topic=topic, payload=payload))
        )


MQTT = setup_mqtt()
