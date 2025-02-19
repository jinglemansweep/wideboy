from dynaconf import Validator
from pathlib import Path

VALIDATORS = [
    # General
    Validator("GENERAL.DEVICE_ID", default=None),
    Validator("GENERAL.DEBUG", default=False, cast=bool),
    Validator("GENERAL.LOG_LEVEL", default="info"),  # error, warning, info, debug
    # Display
    Validator(
        "DISPLAY.CANVAS.WIDTH",
        default=768,
        cast=int,
    ),
    Validator(
        "DISPLAY.CANVAS.HEIGHT",
        default=64,
        cast=int,
    ),
    # Home Assistant
    Validator(
        "HOMEASSISTANT.HOST",
        default=None,
        cast=str,
    ),
    Validator(
        "HOMEASSISTANT.PORT",
        default=8123,
        cast=int,
    ),
    Validator(
        "HOMEASSISTANT.TOKEN",
        default=None,
        cast=str,
    ),
    # MQTT
    Validator(
        "MQTT.HOST",
        required=True,
        cast=str,
    ),
    Validator(
        "MQTT.PORT",
        default=1883,
        cast=int,
    ),
    Validator(
        "MQTT.TOPIC_PREFIX.APP",
        default="wideboy",
        cast=str,
    ),
    Validator(
        "MQTT.TOPIC_PREFIX.HOMEASSISTANT.DEFAULT",
        default="homeassistant",
        cast=str,
    ),
    Validator(
        "MQTT.TOPIC_PREFIX.HOMEASSISTANT.STATESTREAM",
        default="homeassistant/statestream",
        cast=str,
    ),
    Validator(
        "MQTT.USER",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT.PASSWORD",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT.KEEPALIVE",
        default=60,
        cast=int,
    ),
    Validator(
        "MQTT.LOG_MESSAGES",
        default=False,
        cast=bool,
    ),
    # SCENES
    Validator(
        "SCENES.FILE",
        default="scenes/default.yml",
        cast=str,
    ),
    # PATHS
    Validator(
        "PATHS.IMAGES_ICONS",
        default="images/icons",
        cast=Path,
    ),
    Validator(
        "PATHS.IMAGES_BACKGROUNDS",
        default="images/backgrounds",
        cast=Path,
    ),
    Validator(
        "PATHS.IMAGES_SPRITES",
        default="images/sprites",
        cast=Path,
    ),
    Validator(
        "PATHS.IMAGES_WEATHER",
        default="images/weather",
        cast=Path,
    ),
    Validator("PATHS.IMAGES_SCREENSHOTS", default="images/screenshots", cast=Path),
    # LED DISPLAY MATRIX
    Validator(
        "DISPLAY.MATRIX.ENABLED",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.GPIO_MAPPING",
        default="regular",
        cast=str,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.ROWS",
        default=64,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.COLS",
        default=256,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.CHAIN",
        default=1,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PARALLEL",
        default=3,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.MULTIPLEXING",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PIXEL_MAPPER",
        default="V-mapper",
        cast=str,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PWM_BITS",
        default=8,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.BRIGHTNESS",
        default=50,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.SCAN_MODE",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.ROW_ADDR_TYPE",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.SHOW_REFRESH",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.LIMIT_REFRESH",
        default=None,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.INVERSE",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.RGB_SEQUENCE",
        default="RGB",
        cast=str,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PWM_LSB_NANOSECONDS",
        default=200,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PWM_DITHER_BITS",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.NO_HARDWARE_PULSE",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.PANEL_TYPE",
        default=None,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.SLOWDOWN_GPIO",
        default=4,
        cast=int,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.DAEMON",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY.MATRIX.DRIVER.NO_DROP_PRIVS",
        default=True,
        cast=bool,
    ),
]
