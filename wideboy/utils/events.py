import json
import logging
import pygame
import sys

from wideboy.constants import (
    EVENT_EPOCH_SECOND,
    EVENT_EPOCH_MINUTE,
    EVENT_EPOCH_HOUR,
    EVENT_MQTT_MESSAGE,
    EVENT_MASTER_POWER,
    EVENT_MASTER_BRIGHTNESS,
    EVENT_SCENE_NEXT,
)
from wideboy.mqtt import MQTT
from wideboy.state import STATE
from wideboy.scenes.manager import SceneManager
from wideboy.utils.helpers import EpochEmitter

logger = logging.getLogger("utils.events")

epoch_emitter = EpochEmitter()


def handle_events(
    events: list[pygame.event.Event], matrix: any, scene_manager: SceneManager
) -> None:
    handle_state_events(events, matrix, scene_manager)
    handle_mqtt_events(events)
    handle_pygame_events(events)
    handle_epoch_events(events)


def handle_state_events(
    events: list[pygame.event.Event], matrix: any, scene_manager: SceneManager
) -> None:
    for event in events:
        if event.type == EVENT_MASTER_POWER:
            STATE.power = event.value
            MQTT.publish(
                "master/state",
                dict(
                    state="ON" if STATE.power else "OFF",
                    brightness=STATE.brightness,
                ),
            )
        if event.type == EVENT_MASTER_BRIGHTNESS:
            STATE.brightness = event.value
            if matrix:
                matrix.brightness = (STATE.brightness / 255) * 100
            MQTT.publish(
                "master/state",
                dict(
                    state="ON" if STATE.power else "OFF",
                    brightness=STATE.brightness,
                ),
            )
        if event.type == EVENT_SCENE_NEXT:
            scene_manager.next_scene()


def handle_mqtt_events(events: list[pygame.event.Event]):
    for event in events:
        if event.type == EVENT_MQTT_MESSAGE:
            if event.topic.endswith("master/set"):
                try:
                    payload = json.loads(event.payload)
                except Exception as e:
                    logger.warn("hass:mqtt:event error={e}")
                if "state" in payload:
                    pygame.event.post(
                        pygame.event.Event(
                            EVENT_MASTER_POWER, value=payload["state"] == "ON"
                        )
                    )
                if "brightness" in payload:
                    pygame.event.post(
                        pygame.event.Event(
                            EVENT_MASTER_BRIGHTNESS, value=payload["brightness"]
                        )
                    )
            if event.topic.endswith("scene_next/set"):
                pygame.event.post(pygame.event.Event(EVENT_SCENE_NEXT))


def handle_epoch_events(events: list[pygame.event.Event]) -> None:
    epochs = epoch_emitter.check()
    if epochs.get("new_sec"):
        pygame.event.post(
            pygame.event.Event(EVENT_EPOCH_SECOND, unit=epochs.get("sec"))
        )
    if epochs.get("new_min"):
        pygame.event.post(
            pygame.event.Event(EVENT_EPOCH_MINUTE, unit=epochs.get("min"))
        )
    if epochs.get("new_hour"):
        pygame.event.post(pygame.event.Event(EVENT_EPOCH_HOUR, unit=epochs.get("hour")))


def handle_pygame_events(events: list[pygame.event.Event]) -> None:
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
