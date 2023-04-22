import json
import logging
import pygame
from dynaconf import Dynaconf
from pygame import Event
from typing import Any, Optional
import paho.mqtt.client as mqtt

from wideboy.config import settings
from wideboy.constants import (
    EVENT_MQTT_MESSAGE_RECEIVED,
    EVENT_MQTT_MESSAGE_SEND,
    EVENT_ACTION_A,
    EVENT_ACTION_B,
    EVENT_NOTIFICATION_RECEIVED,
    EVENT_MASTER_BRIGHTNESS,
    EVENT_MASTER_POWER,
    EVENT_SCENE_MANAGER_NEXT,
    EVENT_SCENE_MANAGER_SELECT,
)
from wideboy.config import DEVICE_ID


logger = logging.getLogger("mqtt")

MQTT_TOPIC_PREFIX = settings.mqtt.topic_prefix


class MQTTClient:
    def __init__(
        self,
        options: Dynaconf,
        keepalive: int = 60,
    ) -> None:
        self.options = options
        logger.info(
            f"MQTT: host={self.options.host} port={self.options.port} user={self.options.user} password={'*' * len(self.options.password or 0)}"
        )
        self.client: mqtt.Client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connect()

    def connect(self) -> None:
        logger.debug("MQTT: connect")
        if self.options.user is not None:
            self.client.username_pw_set(self.options.user, self.options.password)
        self.client.connect(
            self.options.host, self.options.port, self.options.keepalive
        )
        # self.client.loop_start()

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
        self.subscribe(f"{MQTT_TOPIC_PREFIX}/{DEVICE_ID}/#", 0)

    def _on_message(self, client, userdata, msg):
        topic, payload = str(msg.topic), msg.payload.decode("utf-8")
        logger.debug(
            f"mqtt:message topic={topic} payload={payload} userdata={userdata}"
        )
        pygame.event.post(
            Event(EVENT_MQTT_MESSAGE_RECEIVED, dict(topic=topic, payload=payload))
        )
