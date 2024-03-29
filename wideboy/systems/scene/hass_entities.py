import json
import logging
from paho.mqtt.client import Client as MQTTClient
from typing import Any, Dict
from ...entities import AppState
from ...homeassistant import (
    ButtonEntity,
    LightEntity,
    NumberEntity,
    SelectEntity,
    SwitchEntity,
    TextEntity,
    strip_quotes,
    to_hass_bool,
)

logger = logging.getLogger(__name__)


class MasterPowerLight(LightEntity):
    name: str = "master"
    description: str = "Master"
    initial_state: Dict[str, Any] = {"state": "ON", "brightness": 128}
    options: Dict[str, Any] = {
        "brightness": True,
        "supported_color_mode": ["brightness"],
    }

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        payload_dict = json.loads(payload)
        app_state.master_power = payload_dict["state"] == "ON"
        if "brightness" in payload_dict:
            app_state.master_brightness = int(payload_dict["brightness"])
        logger.debug(
            f"sys.hass.entities.light.master: state={app_state.master_power} brightness={app_state.master_brightness}"
        )
        client.publish(
            state_topic,
            json.dumps(
                {
                    "state": to_hass_bool(app_state.master_power),
                    "brightness": app_state.master_brightness,
                }
            ),
            qos=1,
        )


class ModeSelect(SelectEntity):
    name: str = "mode"
    description: str = "Mode"
    initial_state: str = "default"
    options: Dict[str, Any] = {
        "options": ["city", "default", "diffusion", "galaxy", "vinyl"],
    }

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        app_state.scene_mode = payload
        logger.debug(
            f"sys.hass.entities.select.scene_mode: state={app_state.scene_mode}"
        )
        client.publish(
            state_topic,
            app_state.scene_mode,
            qos=1,
        )


class Clock24HourSwitch(SwitchEntity):
    name: str = "clock_24_hour"
    description: str = "24h Clock"
    initial_state: str = "ON"

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        app_state.clock_24_hour = payload == "ON"
        logger.debug(
            f"sys.hass.entities.clock_24_hour: state={app_state.clock_24_hour}"
        )
        client.publish(
            state_topic,
            to_hass_bool(app_state.clock_24_hour),
            qos=1,
        )


class BackgroundTintLight(LightEntity):
    name: str = "background_tint"
    description: str = "Background Tint"
    initial_state: Dict[str, Any] = {
        "state": "OFF",
        "brightness": 255,
        "color": {"r": 255, "g": 255, "b": 255},
    }
    options: Dict[str, Any] = {
        "brightness": True,
        "supported_color_modes": ["rgb"],
        "color_mode": True,
    }

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        payload_dict = json.loads(payload)
        app_state.tint_enabled = payload_dict["state"] == "ON"
        if "brightness" in payload_dict:
            app_state.tint_brightness = int(payload_dict["brightness"])
        if "color" in payload_dict:
            app_state.tint_color = (
                int(payload_dict["color"]["r"]),
                int(payload_dict["color"]["g"]),
                int(payload_dict["color"]["b"]),
            )
        logger.debug(
            f"sys.hass.entities.light.background_tint: enabled={app_state.tint_enabled} color={app_state.tint_color} brightness={app_state.tint_brightness}"
        )
        client.publish(
            state_topic,
            json.dumps(
                {
                    "state": to_hass_bool(app_state.tint_enabled),
                    "brightness": app_state.tint_brightness,
                    "color_mode": "rgb",
                    "color": {
                        "r": app_state.tint_color[0],
                        "g": app_state.tint_color[1],
                        "b": app_state.tint_color[2],
                    },
                }
            ),
            qos=1,
        )


class BackgroundIntervalNumber(NumberEntity):
    name: str = "slideshow_interval"
    description: str = "Slideshow Interval"
    # initial_state: int = 10
    options: Dict[str, Any] = {
        "device_class": "duration",
        "step": 1,
        "min": 10,
        "max": 600,
        "unit_of_measurement": "s",
    }

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        app_state.slideshow_interval = int(payload)
        logger.debug(
            f"sys.hass.entities.number.slideshow_interval: state={app_state.slideshow_interval}"
        )
        client.publish(
            state_topic,
            app_state.slideshow_interval,
            qos=1,
        )


class MessageText(TextEntity):
    name: str = "message"
    description: str = "Message"
    initial_state: str = "Hello"

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        app_state.text_message = payload
        logger.debug(f"sys.hass.entities.text.message: state={app_state.text_message}")
        client.publish(
            state_topic,
            strip_quotes(app_state.text_message),
            qos=1,
        )


class StateLogButton(ButtonEntity):
    name: str = "state_log"
    description: str = "Log State"

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        logger.debug("sys.hass.entities.button.state_log: press")
        logger.info(f"app_state: {app_state}")


class ScreenshotButton(ButtonEntity):
    name: str = "screenshot"
    description: str = "Screenshot"

    def callback(
        self,
        client: MQTTClient,
        app_state: AppState,
        state_topic: str,
        payload: str,
    ) -> None:
        logger.debug("sys.hass.entities.button.screenshot: press")
        app_state.screenshot = True


ENTITIES = [
    MasterPowerLight,
    ModeSelect,
    Clock24HourSwitch,
    BackgroundTintLight,
    BackgroundIntervalNumber,
    MessageText,
    StateLogButton,
    ScreenshotButton,
]
