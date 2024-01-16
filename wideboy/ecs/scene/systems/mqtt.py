from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient
from pygame.event import Event, post as post_event
from typing import Any
from ..consts import EVENT_HASS_ENTITY_UPDATE
from ..entities import AppState, MQTTService


class SysMQTT(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.client = MQTTClient()

    def start(self):
        self.client.username_pw_set("mqtt", "password")
        self.client.on_message = self._on_message
        self.client.connect("hass.home", 1883, 60)
        listeners = []  # [self.debug_listener]
        self.entities.add(MQTTService(client=self.client, listeners=listeners))

    def update(self):
        self.client.loop(timeout=0.001)

    def debug_listener(self, topic: str, payload: str, client: MQTTClient) -> None:
        print(f"sys.mqtt.message: topic: {topic}, payload: {payload}")

    def _on_message(self, client: MQTTClient, userdata: Any, message: Any):
        mqtt_service = next(self.entities.get_by_class(MQTTService))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        for listener in mqtt_service.listeners:
            listener(topic, payload, client)


class SysHomeAssistant(System):
    statestream_topic_prefix = "homeassistant/statestream"

    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.mqtt = None

    def start(self):
        self.mqtt = next(self.entities.get_by_class(MQTTService))
        self.mqtt.listeners.append(self.on_mqtt_message)
        self.mqtt.client.subscribe(f"{self.statestream_topic_prefix}/#")

    def on_mqtt_message(self, topic, payload, client):
        # STATESTREAM
        if topic.startswith(f"{self.statestream_topic_prefix}/"):
            app_state = next(self.entities.get_by_class(AppState))
            parts = topic[len(self.statestream_topic_prefix) :].split("/")
            device_class, entity_id, attr = parts[1], parts[-2], parts[-1]
            entity_id_full = f"{device_class}.{entity_id}"
            post_event(
                Event(
                    EVENT_HASS_ENTITY_UPDATE,
                    dict(entity_id=entity_id_full, attribute=attr, payload=payload),
                )
            )
            if entity_id_full not in app_state.hass_state:
                app_state.hass_state[entity_id_full] = dict()
            app_state.hass_state[entity_id_full][attr] = payload
