import datetime
import logging
from dynaconf import Dynaconf
from ecs_pattern import EntityManager, System
from pygame.constants import KEYDOWN, KEYUP, QUIT, K_UP, K_DOWN, K_ESCAPE
from pygame.event import get as get_pygame_events
from typing import Optional
from ..entities import AppState
from ..consts import EventTypes

logger = logging.getLogger(__name__)


class SysBoot(System):
    def __init__(
        self,
        entities: EntityManager,
        config: Dynaconf,
    ) -> None:
        self.entities = entities
        self.config = config

    def start(self) -> None:
        logger.info("Boot system starting...")
        self.entities.init()


class SysEvents(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Events system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        pygame_events = get_pygame_events()
        self.app_state.events = [(event.type, event.dict) for event in pygame_events]
        # logger.debug(
        #     f"sys.events.update: events={len(self.events)} pygame_events={len(pygame_events)}"
        # )
        if len(self.app_state.events) > 0:
            logger.debug(f"sys.events.update: {self.app_state.events}")


class SysClock(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.now = datetime.datetime.now()

    def start(self) -> None:
        logger.info("Clock system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        now = datetime.datetime.now()
        if now.second != self.now.second:
            app_state = next(self.entities.get_by_class(AppState))
            app_state.time_now = now
            self.app_state.events.append(
                (EventTypes.EVENT_CLOCK_NEW_SECOND, dict(unit=now.second, now=now))
            )
            if now.second == 0 and now.minute != self.now.minute:
                self.app_state.events.append(
                    (EventTypes.EVENT_CLOCK_NEW_MINUTE, dict(unit=now.minute, now=now))
                )
                if now.minute == 0 and now.hour != self.now.hour:
                    self.app_state.events.append(
                        (EventTypes.EVENT_CLOCK_NEW_HOUR, dict(unit=now.hour, now=now))
                    )
            self.now = now


class SysInput(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.event_types = (KEYDOWN, KEYUP, QUIT)  # Whitelist
        self.app_state: Optional[AppState] = None

    def start(self) -> None:
        logger.info("Input system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        if not self.app_state:
            return
        for event in get_pygame_events(self.event_types):
            event_type = event.type
            event_key = getattr(event, "key", None)
            # Quit App
            if (event_type == KEYDOWN and event_key == K_ESCAPE) or event_type == QUIT:
                self.app_state.running = False
            # Up/Down
            if event_type == KEYDOWN and event_key in (K_UP, K_DOWN):
                logger.debug("Up/Down", event_key)


class SysDebug(System):
    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities

    def start(self) -> None:
        logger.info("Debug system starting...")
        self.app_state = next(self.entities.get_by_class(AppState))

    def update(self) -> None:
        for event_type, event_payload in self.app_state.events:
            if event_type == EventTypes.EVENT_DEBUG_LOG:
                logger.debug(f"sys.debug.log: {event_payload['msg']}")
            if event_type == EventTypes.EVENT_CLOCK_NEW_SECOND:
                logger.debug(f"sys.debug.clock: {event_payload['now']}")
