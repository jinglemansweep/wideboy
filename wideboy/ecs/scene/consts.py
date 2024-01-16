import enum

FPS_MAX = 100
FPS_CORR = 24 / FPS_MAX


class EventsEnum(enum.Enum):
    HASS_ENTITY_UPDATE = enum.auto()
