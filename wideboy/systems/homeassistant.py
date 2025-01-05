import json
import logging
import websocket
from ecs_pattern import EntityManager, System
from typing import List
from ..consts import EventTypes
from ..entities import AppState, Cache


logger = logging.getLogger(__name__)


class SysHomeAssistantWebsocket(System):

    REQ_IDX_GET_STATE = 1
    REQ_IDX_SUBSCRIBE = 11

    def __init__(self, entities: EntityManager) -> None:
        self.entities = entities
        self.app_state: AppState
        self.cache: Cache
        self.ws = websocket.WebSocket()
        self.subscription_ids: List[int] = []

    def start(self) -> None:
        logger.info("HASS WS System Started")
        # Get AppState and Cache
        self.app_state = next(self.entities.get_by_class(AppState))
        if not self.app_state:
            raise Exception("AppState not found")
        self.cache = next(self.entities.get_by_class(Cache))
        if not self.cache:
            raise Exception("Cache not found")
        config = self.app_state.config.homeassistant
        # Connect to websocket API
        self.ws.connect(f"ws://{config.host}:{config.port}/api/websocket")
        self.ws.settimeout(0.01)
        # Login
        auth = {"type": "auth", "access_token": config.token}
        self.ws.send(json.dumps(auth))
        # Get all entity states
        state_message = {"id": self.REQ_IDX_GET_STATE, "type": "get_states"}
        self.ws.send(json.dumps(state_message))
        # Subscribe to watched entity changes
        for idx, entity_id in enumerate(config.entities):
            subscription_idx = self.REQ_IDX_SUBSCRIBE + idx
            subscribe_message = {
                "id": subscription_idx,
                "type": "subscribe_trigger",
                "trigger": {"platform": "state", "entity_id": entity_id},
            }
            self.ws.send(json.dumps(subscribe_message))
            self.subscription_ids.append(subscription_idx)

    def update(self) -> None:
        try:
            message = self.ws.recv()
            if message:
                parsed = json.loads(message)
                # Handle result responses
                if parsed["type"] == "result":
                    if parsed["id"] == self.REQ_IDX_GET_STATE:
                        # Cache all entity states
                        for entity in parsed["result"]:
                            self.cache.hass_entities[entity["entity_id"]] = entity
                if parsed["type"] == "event" and parsed["id"] in self.subscription_ids:
                    # Cache entity state updates
                    entity_id = parsed["event"]["variables"]["trigger"]["entity_id"]
                    state = parsed["event"]["variables"]["trigger"]["to_state"]
                    logger.debug(
                        f"sys.hassws.event: entity_id={entity_id} state={state}"
                    )
                    self.cache.hass_entities[entity_id] = state
                    # Send entity update event
                    self.app_state.events.append(
                        (
                            EventTypes.EVENT_HASS_WS_ENTITY_UPDATE,
                            {
                                "entity_id": entity_id,
                            },
                        )
                    )
        except Exception:
            pass

    def stop(self) -> None:
        self.ws.close()
