from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class HomeAssistantService:
    def __init__(
        self,
        host: str,
        port: int,
        token: str,
        entity_ids: list[str],
        ssl: bool = False,
        poll_interval: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.token = token
        self.entity_ids = entity_ids
        self.ssl = ssl
        self.poll_interval = poll_interval

        self._base_url = f"{'https' if ssl else 'http'}://{host}:{port}"
        self._ws_url = f"{'wss' if ssl else 'ws'}://{host}:{port}/api/websocket"
        self._headers = {"Authorization": f"Bearer {token}"}

        self._snapshot: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._ws_thread: threading.Thread | None = None
        self._poll_thread: threading.Thread | None = None
        self._running = False
        self._connected = False
        self._subscribed = False

    @property
    def snapshot(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return dict(self._snapshot)

    def start(self) -> None:
        if not self.host or not self.token:
            logger.warning("HA not configured (host/token empty), skipping")
            return
        self._running = True
        self._ws_thread = threading.Thread(target=self._ws_loop, daemon=True, name="ha-ws")
        self._ws_thread.start()
        logger.info("HA service started (WebSocket thread)")

    def stop(self) -> None:
        self._running = False
        if self._ws_thread:
            self._ws_thread.join(timeout=3)
        if self._poll_thread:
            self._poll_thread.join(timeout=3)
        logger.info("HA service stopped")

    def _ws_loop(self) -> None:
        while self._running:
            try:
                self._ws_connect()
            except Exception:
                logger.exception("HA WebSocket error, reconnecting in 5s")
                time.sleep(5)

    _PING_INTERVAL = 30
    _PING_TIMEOUT = 90

    def _ws_connect(self) -> None:
        import websocket

        ws = websocket.WebSocket()
        ws.connect(self._ws_url)
        ws.settimeout(self._PING_INTERVAL)

        auth_msg = ws.recv()
        auth_data = json.loads(auth_msg)
        if auth_data.get("type") != "auth_required":
            logger.error("Unexpected WS message: %s", auth_data)
            ws.close()
            return

        ws.send(json.dumps({"type": "auth", "access_token": self.token}))
        auth_result = json.loads(ws.recv())
        if auth_result.get("type") != "auth_ok":
            logger.error("HA auth failed: %s", auth_result)
            ws.close()
            return

        logger.info("HA WebSocket authenticated")
        self._connected = True

        self._seed_states()

        self._subscribed = False
        if self.entity_ids:
            subscribe_msg = {
                "id": 1,
                "type": "subscribe_entities",
                "entity_ids": self.entity_ids,
            }
            ws.send(json.dumps(subscribe_msg))
            logger.info("Subscribing to %d entities", len(self.entity_ids))
        else:
            self._subscribed = True

        ping_id = 2
        last_msg_time = time.monotonic()

        try:
            while self._running:
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException:
                    elapsed = time.monotonic() - last_msg_time
                    if elapsed > self._PING_TIMEOUT:
                        logger.warning("HA WebSocket idle for %.0fs, reconnecting", elapsed)
                        break
                    try:
                        ws.send(json.dumps({"id": ping_id, "type": "ping"}))
                        ping_id += 1
                    except Exception:
                        logger.warning("HA ping failed, reconnecting")
                        break
                    continue
                except Exception:
                    break
                if not raw:
                    continue
                last_msg_time = time.monotonic()
                msg = json.loads(raw)
                self._handle_ws_message(msg)
        finally:
            self._connected = False
            ws.close()

    def _seed_states(self) -> None:
        for eid in self.entity_ids:
            try:
                resp = requests.get(
                    f"{self._base_url}/api/states/{eid}",
                    headers=self._headers,
                    timeout=5,
                )
                if resp.ok:
                    data = resp.json()
                    with self._lock:
                        self._snapshot[eid] = data
                else:
                    logger.warning("Failed to seed %s: %s", eid, resp.status_code)
            except Exception:
                logger.warning("Failed to seed %s", eid, exc_info=True)

    @staticmethod
    def _normalize_entity(state_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "state": state_data.get("s", state_data.get("state")),
            "attributes": state_data.get("a", state_data.get("attributes", {})),
            "last_changed": state_data.get("lc", state_data.get("last_changed")),
            "last_updated": state_data.get("lu", state_data.get("last_updated")),
            "entity_id": state_data.get("entity_id"),
        }

    def _handle_ws_message(self, msg: dict[str, Any]) -> None:
        msg_type = msg.get("type")
        if msg_type == "result":
            if msg.get("id") == 1 and not self._subscribed:
                self._subscribed = True
                if msg.get("success"):
                    result = msg.get("result")
                    logger.info("HA entity subscription confirmed")
                    if isinstance(result, dict):
                        for entity_id, state_data in result.items():
                            normalized = self._normalize_entity(state_data)
                            normalized["entity_id"] = entity_id
                            with self._lock:
                                self._snapshot[entity_id] = normalized
                            logger.debug(
                                "HA entity seeded from subscription: %s = %s",
                                entity_id,
                                normalized.get("state"),
                            )
                else:
                    logger.error(
                        "HA entity subscription failed: %s",
                        msg.get("error", "unknown error"),
                    )
        elif msg_type == "event":
            event = msg.get("event", {})
            added = event.get("a", {})
            changed = event.get("c", {})
            if added or changed:
                logger.debug(
                    "HA event: %d added, %d changed entities",
                    len(added),
                    len(changed),
                )
            for entity_id, state_data in added.items():
                normalized = self._normalize_entity(state_data)
                normalized["entity_id"] = entity_id
                with self._lock:
                    self._snapshot[entity_id] = normalized
                logger.debug("HA entity added: %s = %s", entity_id, normalized.get("state"))
            for entity_id, change_data in changed.items():
                if isinstance(change_data, dict) and "+" in change_data:
                    plus = change_data["+"]
                    normalized = self._normalize_entity(plus)
                    with self._lock:
                        existing = self._snapshot.get(entity_id, {})
                        updated = dict(existing)
                        if "state" in normalized and normalized["state"] is not None:
                            updated["state"] = normalized["state"]
                        if "attributes" in normalized and normalized["attributes"]:
                            updated["attributes"] = {
                                **updated.get("attributes", {}),
                                **normalized["attributes"],
                            }
                        self._snapshot[entity_id] = updated
                    logger.debug("HA entity changed: %s = %s", entity_id, normalized.get("state"))
                else:
                    logger.debug(
                        "HA entity change without '+' delta: %s = %s",
                        entity_id,
                        change_data,
                    )
        else:
            logger.debug("HA unhandled message type: %s", msg_type)

    def _start_polling_fallback(self) -> None:
        self._poll_thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="ha-poll"
        )
        self._poll_thread.start()

    def _poll_loop(self) -> None:
        while self._running:
            for eid in self.entity_ids:
                try:
                    resp = requests.get(
                        f"{self._base_url}/api/states/{eid}",
                        headers=self._headers,
                        timeout=5,
                    )
                    if resp.ok:
                        data = resp.json()
                        with self._lock:
                            self._snapshot[eid] = data
                except Exception:
                    pass
            time.sleep(self.poll_interval)
