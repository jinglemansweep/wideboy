from ecs_pattern import EntityManager, System
from paho.mqtt.client import Client as MQTTClient
from pygame.event import Event, post as post_event
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
        self.client.subscribe("homeassistant/statestream/#")
        self.entities.add(MQTTService(client=self.client))

    def update(self):
        self.client.loop(timeout=0.001)

    def _on_message(self, client, userdata, message):
        topic_prefix = "homeassistant/statestream"
        app_state = next(self.entities.get_by_class(AppState))
        if message.topic.startswith(f"{topic_prefix}/") and message.payload:
            parts = message.topic[len(topic_prefix) :].split("/")
            payload = message.payload.decode("utf-8")
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


class SysHomeAssistant(System):
    def __init__(self, entities: EntityManager):
        self.entities = entities
        self.mqtt = None

    def start(self):
        self.mqtt = next(self.entities.get_by_class(MQTTService))

    def update(self):
        print("HASS", self.mqtt.client)
