from enum import Enum, auto

FPS_MAX = 50
FPS_CORR = 24 / FPS_MAX


class EventTypes(Enum):
    EVENT_DEBUG_LOG = auto()
    EVENT_CLOCK_NEW_SECOND = auto()
    EVENT_CLOCK_NEW_MINUTE = auto()
    EVENT_CLOCK_NEW_HOUR = auto()
    EVENT_HASS_ENTITY_UPDATE = auto()
