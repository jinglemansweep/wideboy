import json
import logging
import pygame

from pygame import Event
from typing import Any, Dict
import paho.mqtt.client as mqtt

from wideboy.config import settings
from wideboy.constants import (
    EVENT_MQTT_MESSAGE_RECEIVED,
)


logger = logging.getLogger("mqtt")


class MQTTClient:
    def __init__(self, device_id: str) -> None:
        logger.info(
            f"mqtt:init device_id={device_id} \
            host={settings.mqtt.host} port={settings.mqtt.port} \
            user={settings.mqtt.user} password={'*' * len(settings.mqtt.password) or 0}"
        )
        self.device_id = device_id
        self.client: mqtt.Client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connect()

    def connect(self) -> None:
        logger.debug("mqtt:connecting")
        if settings.mqtt.user is not None:
            self.client.username_pw_set(settings.mqtt.user, settings.mqtt.password)
        self.client.connect(
            settings.mqtt.host, settings.mqtt.port, settings.mqtt.keepalive
        )

    def loop(self, timeout: float = 0.1) -> None:
        self.client.loop(timeout)

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        retain: bool = True,
        qos: int = 1,
    ) -> mqtt.MQTTMessageInfo:
        json_payload = json.dumps(payload)
        logger.debug(
            f"mqtt:publish topic={topic} payload={json_payload} retain={retain} qos={qos}"
        )
        return self.client.publish(topic, json_payload, retain=retain, qos=qos)

    def subscribe(self, topic: str, args: Any) -> None:
        logger.debug(f"mqtt:subscribe topic={topic}")
        self.client.subscribe(topic, args)

    def _on_connect(
        self, client: mqtt.Client, userdata: Any, flags: Any, rc: Any
    ) -> None:
        logger.info(
            f"mqtt:connected connected={client.is_connected()} userdata={userdata} flags={flags} rc={str(rc)}"
        )
        self.subscribe("homeassistant/#", 0)
        # DISABLED, could be too slow
        # self.subscribe(f"{settings.mqtt.topic_prefix}/{self.device_id}/#", 0)

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: Any) -> None:
        topic, payload = str(msg.topic), msg.payload.decode("utf-8")
        # logger.debug(
        #     f"mqtt:message_received topic={topic} payload={payload} userdata={userdata}"
        # )
        pygame.event.post(
            Event(EVENT_MQTT_MESSAGE_RECEIVED, dict(topic=topic, payload=payload))
        )
