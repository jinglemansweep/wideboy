from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import paho.mqtt.client as mqtt

from ..config import MqttConfig, Settings

logger = logging.getLogger(__name__)


class MqttHassService:
    def __init__(
        self,
        config: MqttConfig,
        state: Any,
        settings: Settings,
    ) -> None:
        self._config = config
        self._state = state
        self._settings = settings
        self._client: mqtt.Client | None = None
        self._base_topic = f"{config.device_id}"
        self._discovery_prefix = config.discovery_prefix

        self._current_state: dict[str, Any] = {
            "state": "ON",
            "brightness": 255,
            "fg_brightness": int(state.brightness.foreground_level * 100),
            "scene": Path(settings.scenes.file).stem,
            "effect": self._get_current_effect(),
            "effect_speed": 1.0,
            "tag": self._get_current_tag(),
            "palette": self._get_current_palette(),
        }

    def _get_current_effect(self) -> str:
        bg = self._state.background
        if hasattr(bg, "_effect_name"):
            return bg._effect_name
        if hasattr(bg, "_backgrounds"):
            for child in bg._backgrounds:
                if hasattr(child, "_effect_name"):
                    return child._effect_name
        return "plasma"

    def _get_current_tag(self) -> str:
        bg = self._state.background
        if hasattr(bg, "tag_filter"):
            return bg.tag_filter or "all"
        return "all"

    def _get_current_palette(self) -> str:
        bg = self._state.background
        if hasattr(bg, "_resolver") and bg._resolver:
            return bg._resolver.base_name
        if hasattr(bg, "_backgrounds"):
            from ..backgrounds.composite import CompositeBackground

            if isinstance(bg, CompositeBackground):
                current = bg._backgrounds[bg._current_index]
                if hasattr(current, "get_palette"):
                    return current.get_palette()
        return "neon"

    def _get_available_effects(self) -> list[str]:
        try:
            from ..backgrounds.procedural import EFFECTS

            return ["auto"] + sorted(EFFECTS.keys())
        except ImportError:
            return ["auto"]

    def _get_available_tags(self) -> list[str]:
        try:
            from ..backgrounds.procedural import get_all_tags

            return ["all"] + get_all_tags()
        except ImportError:
            return ["all"]

    def _get_available_palettes(self) -> list[str]:
        try:
            from pathlib import Path

            from ..render.palette import BUILTIN_PALETTES

            names = set(BUILTIN_PALETTES.keys())
            if Path("palettes.yml").exists():
                from ..render.palette import load_palettes

                names.update(load_palettes("palettes.yml").keys())
            return sorted(names)
        except ImportError:
            return []

    def _get_available_scenes(self) -> list[str]:
        scenes_dir = Path("scenes")
        if not scenes_dir.exists():
            return []
        return sorted(p.stem for p in scenes_dir.glob("*.yml"))

    def _device_info(self) -> dict:
        return {
            "identifiers": [self._config.device_id],
            "name": self._config.device_name,
            "manufacturer": "wideboy",
            "model": "768x64 LED Matrix",
        }

    def _discovery_payload(self, component: str, object_id: str) -> dict:
        base = {
            "~": f"{self._base_topic}/{object_id}",
            "unique_id": f"{self._config.device_id}_{object_id}",
            "name": object_id.replace("_", " ").title(),
            "device": self._device_info(),
            "availability_topic": f"{self._base_topic}/status",
        }

        if component == "light":
            base.update(
                {
                    "state_topic": "~/state",
                    "command_topic": "~/set",
                    "brightness": True,
                    "brightness_scale": 255,
                    "schema": "json",
                    "state_value_template": "{{ value_json.state }}",
                    "brightness_value_template": "{{ value_json.brightness }}",
                }
            )
        elif component == "number":
            base.update(
                {
                    "state_topic": "~/state",
                    "command_topic": "~/set",
                }
            )
            if object_id in ("fg_brightness",):
                base.update({"min": 0, "max": 100, "step": 1, "unit_of_measurement": "%"})
            elif object_id == "effect_speed":
                base.update({"min": 0.1, "max": 5.0, "step": 0.1})
        elif component == "select":
            base.update(
                {
                    "state_topic": "~/state",
                    "command_topic": "~/set",
                }
            )

        return base

    def _publish_discovery(self) -> None:
        if not self._client:
            return

        entities = [
            ("light", "light"),
            ("number", "fg_brightness"),
            ("number", "effect_speed"),
            ("select", "scene"),
            ("select", "effect"),
            ("select", "tag"),
            ("select", "palette"),
        ]

        for component, object_id in entities:
            payload = self._discovery_payload(component, object_id)

            if component == "select":
                if object_id == "scene":
                    payload["options"] = self._get_available_scenes()
                elif object_id == "effect":
                    payload["options"] = self._get_available_effects()
                elif object_id == "tag":
                    payload["options"] = self._get_available_tags()
                elif object_id == "palette":
                    payload["options"] = self._get_available_palettes()

            topic = (
                f"{self._discovery_prefix}/{component}/{self._config.device_id}/{object_id}/config"
            )
            self._client.publish(topic, json.dumps(payload), retain=True)
            logger.debug("Published discovery: %s", topic)

    def _publish_state(self, object_id: str) -> None:
        if not self._client:
            return

        state_topic = f"{self._base_topic}/{object_id}/state"

        if object_id == "light":
            payload = json.dumps(
                {
                    "state": self._current_state["state"],
                    "brightness": self._current_state["brightness"],
                }
            )
        elif object_id == "fg_brightness":
            payload = str(self._current_state["fg_brightness"])
        elif object_id == "effect_speed":
            payload = str(self._current_state["effect_speed"])
        elif object_id == "scene":
            payload = self._current_state["scene"]
        elif object_id == "effect":
            payload = self._current_state["effect"]
        elif object_id == "tag":
            payload = self._current_state["tag"]
        elif object_id == "palette":
            payload = self._current_state["palette"]
        else:
            return

        self._client.publish(state_topic, payload, retain=True)

    def _publish_all_states(self) -> None:
        for object_id in (
            "light",
            "fg_brightness",
            "effect_speed",
            "scene",
            "effect",
            "tag",
            "palette",
        ):
            self._publish_state(object_id)

    async def connect(self) -> None:
        cfg = self._config

        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=cfg.device_id,
        )

        if cfg.username:
            self._client.username_pw_set(cfg.username, cfg.password)

        self._client.will_set(
            f"{self._base_topic}/status",
            payload="offline",
            qos=1,
            retain=True,
        )

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                logger.info("MQTT connected to %s:%d", cfg.host, cfg.port)
                client.subscribe(f"{self._base_topic}/+/set")
                client.publish(
                    f"{self._base_topic}/status",
                    "online",
                    qos=1,
                    retain=True,
                )
                self._publish_discovery()
                self._publish_all_states()
            else:
                logger.error("MQTT connect failed: %s", reason_code)

        def on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode("utf-8", errors="replace")
            logger.debug("MQTT recv: %s = %s", topic, payload)
            try:
                self._handle_command(topic, payload)
            except Exception:
                logger.exception("Error handling MQTT command: %s = %s", topic, payload)

        self._client.on_connect = on_connect
        self._client.on_message = on_message

        try:
            self._client.connect(cfg.host, cfg.port, keepalive=60)
            self._client.loop_start()
        except Exception:
            logger.exception("Failed to connect to MQTT broker")

    async def disconnect(self) -> None:
        if self._client:
            self._client.publish(
                f"{self._base_topic}/status",
                "offline",
                qos=1,
                retain=True,
            )
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("MQTT disconnected")

    async def run(self) -> None:
        while True:
            await asyncio.sleep(3600)

    async def drain_commands(self, state: Any) -> None:
        pass

    def _handle_command(self, topic: str, payload: str) -> None:
        parts = topic.split("/")
        if len(parts) < 3:
            return

        object_id = parts[-2]
        action = parts[-1]
        if action != "set":
            return

        logger.info("MQTT command: %s/%s = %s", object_id, action, payload)

        if object_id == "light":
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON for light command: %s", payload)
                return
            logger.info("Light command received: %s", data)
            new_state = data.get("state", self._current_state["state"])
            self._current_state["state"] = new_state
            self._state.master_on = new_state == "ON"

            if "brightness" in data:
                b = int(data["brightness"])
                self._current_state["brightness"] = b
                self._state.master_level = b / 255.0
                self._state.brightness.set_background(self._state.master_level)
                logger.info("Background brightness set to %.2f", self._state.master_level)

            self._publish_state("light")

        elif object_id == "fg_brightness":
            try:
                val = float(payload) / 100.0
            except ValueError:
                return
            self._current_state["fg_brightness"] = int(float(payload))
            self._state.brightness.set_foreground(val)
            self._publish_state("fg_brightness")

        elif object_id == "effect_speed":
            try:
                speed = float(payload)
            except ValueError:
                return
            self._current_state["effect_speed"] = speed
            self._set_effect_speed(speed)
            self._publish_state("effect_speed")

        elif object_id == "scene":
            scene_file = f"scenes/{payload}.yml"
            if not Path(scene_file).exists():
                logger.warning("Scene not found: %s", scene_file)
                return
            self._current_state["scene"] = payload
            self._reload_scene(scene_file)
            self._publish_state("scene")

        elif object_id == "effect":
            self._current_state["effect"] = payload
            self._set_effect(payload)
            self._publish_state("effect")

        elif object_id == "tag":
            tag = payload if payload != "all" else ""
            self._current_state["tag"] = payload
            self._set_tag(tag)
            self._publish_state("tag")

        elif object_id == "palette":
            self._current_state["palette"] = payload
            self._set_palette(payload)
            self._publish_state("palette")

    def _set_effect(self, name: str) -> None:
        bg = self._state.background
        if hasattr(bg, "set_effect"):
            bg.set_effect(name)
            return
        if hasattr(bg, "_backgrounds"):
            from ..backgrounds.composite import CompositeBackground

            if isinstance(bg, CompositeBackground):
                if name == "auto":
                    bg.unlock()
                else:
                    bg.lock_effect(name)

    def _set_tag(self, tag: str) -> None:
        bg = self._state.background
        if hasattr(bg, "set_tag"):
            bg.set_tag(tag)

    def _set_palette(self, name: str) -> None:
        bg = self._state.background
        if hasattr(bg, "set_palette"):
            bg.set_palette(name)
            return
        if hasattr(bg, "_backgrounds"):
            from ..backgrounds.composite import CompositeBackground

            if isinstance(bg, CompositeBackground):
                current = bg._backgrounds[bg._current_index]
                if hasattr(current, "set_palette"):
                    current.set_palette(name)

    def _set_effect_speed(self, speed: float) -> None:
        bg = self._state.background
        if hasattr(bg, "set_speed"):
            bg.set_speed(speed)
            return
        if hasattr(bg, "_backgrounds"):
            from ..backgrounds.composite import CompositeBackground

            if isinstance(bg, CompositeBackground):
                current = bg._backgrounds[bg._current_index]
                if hasattr(current, "set_speed"):
                    current.set_speed(speed)

    def _reload_scene(self, scene_file: str) -> None:
        try:
            from ..core.factory import build_background, build_widgets
            from ..core.scene import load_scene
            from ..render.palette import load_palettes

            scene = load_scene(scene_file)
            palettes = load_palettes("palettes.yml")
            background = build_background(scene, palette_definitions=palettes)
            widgets = build_widgets(
                scene,
                canvas_width=self._settings.display.canvas.width,
                canvas_height=self._settings.display.canvas.height,
            )

            self._state.scene = scene
            self._state.palettes = palettes
            self._state.background = background
            self._state.widgets = widgets
            self._settings.scenes.file = scene_file

            logger.info("Scene reloaded: %s", scene_file)
        except Exception:
            logger.exception("Failed to reload scene: %s", scene_file)
