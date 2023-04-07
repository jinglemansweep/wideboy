import logging
import pygame
from wideboy.constants import (
    EVENT_MASTER_POWER,
    EVENT_MASTER_BRIGHTNESS,
    EVENT_NOTIFICATION_RECEIVED,
    EVENT_MQTT_MESSAGE_SEND,
)
from wideboy.state.store import StateStore
from wideboy.utils.helpers import get_device_id
from wideboy.config import settings

logger = logging.getLogger("state")

STATE = StateStore()
DEVICE_ID = settings.general.device_id or get_device_id()


def handle_state_event(event: pygame.event.Event, matrix: any) -> None:
    if event.type == EVENT_MASTER_POWER:
        STATE.power = event.value
        pygame.event.post(
            pygame.event.Event(
                EVENT_MQTT_MESSAGE_SEND,
                topic="master/state",
                payload=dict(state="ON" if STATE.power else "OFF"),
            ),
        )
    if event.type == EVENT_MASTER_BRIGHTNESS:
        STATE.brightness = event.value
        if matrix:
            matrix.brightness = (STATE.brightness / 255) * 100
        pygame.event.post(
            pygame.event.Event(
                EVENT_MQTT_MESSAGE_SEND,
                topic="master/state",
                payload=dict(
                    state="ON" if STATE.power else "OFF",
                    brightness=STATE.brightness,
                ),
            ),
        )
    if event.type == EVENT_NOTIFICATION_RECEIVED:
        logger.debug(f"message: {event.message}")
        STATE.notifications.append(event.message)
