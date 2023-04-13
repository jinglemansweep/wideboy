import json
import logging
import pygame
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
)
from wideboy.config import DEVICE_ID


logger = logging.getLogger("mqtt")

MQTT_TOPIC_PREFIX = settings.mqtt.topic_prefix


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


MQTT = setup_mqtt()


def handle_mqtt_event(event: pygame.event.Event):
    # Outgoing Message
    if event.type == EVENT_MQTT_MESSAGE_SEND:
        MQTT.publish(
            event.topic,
            event.payload,
            auto_prefix=event.auto_prefix if hasattr(event, "auto_prefix") else True,
        )
    # Incoming Message
    if event.type == EVENT_MQTT_MESSAGE_RECEIVED:
        if event.topic.endswith("master/set"):
            try:
                payload = json.loads(event.payload)
            except Exception as e:
                logger.warn("hass:mqtt:event error={e}")
            if "state" in payload:
                pygame.event.post(
                    Event(EVENT_MASTER_POWER, value=payload["state"] == "ON")
                )
            if "brightness" in payload:
                pygame.event.post(
                    Event(EVENT_MASTER_BRIGHTNESS, value=payload["brightness"])
                )
        if event.topic.endswith("scene_next/set"):
            pygame.event.post(Event(EVENT_SCENE_MANAGER_NEXT))
        if event.topic.endswith("action_a/set"):
            pygame.event.post(Event(EVENT_ACTION_A))
        if event.topic.endswith("action_b/set"):
            pygame.event.post(Event(EVENT_ACTION_B))
        if event.topic.endswith("message/set"):
            pygame.event.post(Event(EVENT_NOTIFICATION_RECEIVED, message=event.payload))
