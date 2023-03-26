import json
import logging
import pygame
from wideboy.scenes.manager import SceneManager
from wideboy.utils.pygame import EVENT_MQTT_MESSAGE
from wideboy.mqtt.homeassistant import HASSEntity

logger = logging.getLogger(__name__)

HASS_MASTER = HASSEntity(
    "master",
    "light",
    dict(brightness=True, color_mode=True, supported_color_modes=["brightness"]),
    initial_state=dict(state="ON", brightness=128),
)

HASS_SELECT_SCENE = HASSEntity(
    "select_scene",
    "select",
    dict(options=["default", "blank"]),
    initial_state=dict(state="default"),
)


def handle_entity_events(events: list[pygame.event.Event], scene_manager: SceneManager):
    for event in events:
        if event.type == EVENT_MQTT_MESSAGE:
            try:
                payload = json.loads(event.payload)
            except json.decoder.JSONDecodeError as e:
                payload = event.payload
            logger.debug(f"entity:mqtt topic={event.topic} payload={payload}")
            if event.topic.endswith("master/set"):
                HASS_MASTER.update(payload)
            if event.topic.endswith("select_scene/set"):
                HASS_SELECT_SCENE.update(payload)
                scene_manager.change_scene(HASS_SELECT_SCENE.state["state"])
