import os
import sys

from dynaconf import Dynaconf, Validator
from pathlib import Path
from pprint import pprint

from wideboy.constants import DYNACONF_ENVVAR_PREFIX

validators = [
    # General
    Validator(
        "GENERAL__REMOTE_URL",
        default="http://wideboy.local",
        cast=str,
    ),
    Validator("GENERAL__DEBUG", default=False, cast=bool),
    Validator(
        "GENERAL__LOG_LEVEL",
        default="info",
        cast=str,
    ),
    Validator(
        "GENERAL__PROFILING",
        default="",
        cast=str,
    ),
    # Display
    Validator(
        "DISPLAY__CANVAS__WIDTH",
        default=768,
        cast=int,
    ),
    Validator(
        "DISPLAY__CANVAS__HEIGHT",
        default=64,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__ENABLED",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY__MATRIX__WIDTH",
        default=256,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__HEIGHT",
        default=192,
        cast=int,
    ),
    # MQTT
    Validator(
        "MQTT__HOST",
        required=True,
        cast=str,
    ),
    Validator(
        "MQTT__PORT",
        default=1883,
        cast=int,
    ),
    Validator(
        "MQTT__TOPIC_PREFIX",
        default="wideboy",
        cast=str,
    ),
    Validator(
        "MQTT__USER",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT__PASSWORD",
        default=None,
        cast=str,
    ),
    # HOME ASSISTANT
    Validator(
        "HOMEASSISTANT__URL",
        default="http://homeassistant.local:8123",
        cast=str,
    ),
    Validator(
        "HOMEASSISTANT__API_TOKEN",
        default=None,
        cast=str,
    ),
    # PATHS
    Validator(
        "PATHS__IMAGES_ICONS",
        default="images/icons",
        cast=Path,
    ),
    Validator(
        "PATHS__IMAGES_BACKGROUNDS",
        default="images/backgrounds",
        cast=Path,
    ),
    # WEATHER
    Validator(
        "WEATHER__FETCH_INTERVAL_MINS",
        default=15,
        cast=int,
    ),
    Validator(
        "WEATHER__LATITUDE",
        default=50.0,
        cast=float,
    ),
    Validator(
        "WEATHER__LONGITUDE",
        default=1.0,
        cast=float,
    ),
    # BACKGROUNDS
    Validator(
        "BACKGROUNDS__CHANGE_INTERVAL_MINS",
        default=10,
        cast=int,
    ),
    # LED DRIVER
    Validator(
        "DISPLAY__MATRIX__DRIVER__GPIO_MAPPING",
        default="regular",
        cast=str,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__ROWS",
        default=64,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__COLS",
        default=64,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__CHAIN",
        default=4,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PARALLEL",
        default=3,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__MULTIPLEXING",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PIXEL_MAPPER",
        default="Rotate:270;Mirror:H",
        cast=str,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PWM_BITS",
        default=7,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__BRIGHTNESS",
        default=50,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__SCAN_MODE",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__ROW_ADDR_TYPE",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__SHOW_REFRESH",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__LIMIT_REFRESH",
        default=None,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__INVERSE",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__RGB_SEQUENCE",
        default="RGB",
        cast=str,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PWM_LSB_NANOSECONDS",
        default=200,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PWM_DITHER_BITS",
        default=0,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__NO_HARDWARE_PULSE",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__PANEL_TYPE",
        default=None,
        cast=str,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__SLOWDOWN_GPIO",
        default=4,
        cast=int,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__DAEMON",
        default=False,
        cast=bool,
    ),
    Validator(
        "DISPLAY__MATRIX__DRIVER__NO_DROP_PRIVS",
        default=False,
        cast=bool,
    ),
]


settings = Dynaconf(
    envvar_prefix=DYNACONF_ENVVAR_PREFIX,
    settings_files=["settings.toml", "secrets.toml"],
    validators=validators,
)


def get_config_env_var(key, default=None):
    return os.environ.get(key, default)


# RPI-RGB-LED-MATRIX

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../lib/rpi-rgb-led-matrix/bindings/python"
        ),
    ),
)
from rgbmatrix import RGBMatrixOptions  # type: ignore

LED_ENABLED = get_config_env_var("LED_ENABLED", "true").lower() == "true"
LED_GPIO_MAPPING = get_config_env_var(
    "LED_GPIO_MAPPING"
)  # regular, adafruit, adafruit-pwm
LED_ROWS = int(get_config_env_var("LED_ROWS", 64))  # 64
LED_COLS = int(get_config_env_var("LED_COLS", 64))  # 64
LED_CHAIN = int(get_config_env_var("LED_CHAIN", 4))  # 4
LED_PARALLEL = int(get_config_env_var("LED_PARALLEL", 3))  # 3
LED_MULTIPLEXING = int(get_config_env_var("LED_MULTIPLEXING", 0))  # 0-18
LED_PIXEL_MAPPER = get_config_env_var(
    "LED_PIXEL_MAPPER", "Rotate:270;Mirror:H"
)  # U-mapper;V-mapper;Rotate:90
LED_PWM_BITS = int(get_config_env_var("LED_PWM_BITS", 7))  # 1-11
LED_BRIGHTNESS = int(get_config_env_var("LED_BRIGHTNESS", 50))  # 0-100
LED_SCAN_MODE = int(get_config_env_var("LED_SCAN_MODE", 0))  # 0,1
LED_ROW_ADDR_TYPE = int(get_config_env_var("LED_ROW_ADDR_TYPE", 0))  # 0-4
LED_SHOW_REFRESH = (
    get_config_env_var("LED_SHOW_REFRESH", "false").lower() == "true"
)  # true/false
LED_LIMIT_REFRESH = int(get_config_env_var("LED_LIMIT_REFRESH", 0))  # 0
LED_INVERSE = get_config_env_var("LED_INVERSE", "false").lower() == "true"  # true/false
LED_RGB_SEQUENCE = get_config_env_var("LED_RGB_SEQUENCE", "RGB")  # RGB, RBG
LED_PWM_LSB_NANOSECONDS = int(get_config_env_var("LED_PWM_LSB_NANOSECONDS", 200))  # 130
LED_PWM_DITHER_BITS = int(get_config_env_var("LED_PWM_DITHER_BITS", 0))  # 0-2
LED_NO_HARDWARE_PULSE = (
    get_config_env_var("LED_NO_HARDWARE_PULSE", "false").lower() == "true"
)  # true/false
LED_PANEL_TYPE = get_config_env_var("LED_PANEL_TYPE")  # FM6126A, FM6127
LED_SLOWDOWN_GPIO = int(get_config_env_var("LED_SLOWDOWN_GPIO", 4))  # 0-4
LED_DAEMON = get_config_env_var("LED_DAEMON", "false").lower() == "true"  # true/false
LED_NO_DROP_PRIVS = (
    get_config_env_var("LED_NO_DROP_PRIVS", "false").lower() == "true"
)  # true/false


matrix_options = RGBMatrixOptions()
driver_settings = settings.display.matrix.driver
print(driver_settings)
if driver_settings.rows:
    matrix_options.rows = driver_settings.rows
if driver_settings.cols:
    matrix_options.cols = driver_settings.cols
if driver_settings.chain:
    matrix_options.chain_length = driver_settings.chain
if driver_settings.parallel:
    matrix_options.parallel = driver_settings.parallel
if driver_settings.row_addr_type:
    matrix_options.row_address_type = driver_settings.row_addr_type
if driver_settings.multiplexing:
    matrix_options.multiplexing = driver_settings.multiplexing
if driver_settings.pixel_mapper:
    matrix_options.pixel_mapper_config = driver_settings.pixel_mapper
if driver_settings.pwm_bits:
    matrix_options.pwm_bits = driver_settings.pwm_bits
if driver_settings.brightness:
    matrix_options.brightness = driver_settings.brightness
if driver_settings.scan_mode:
    matrix_options.scan_mode = driver_settings.scan_mode
if driver_settings.show_refresh:
    matrix_options.show_refresh_rate = driver_settings.show_refresh
if driver_settings.limit_refresh:
    matrix_options.limit_refresh_rate_hz = driver_settings.limit_refresh
if driver_settings.inverse:
    matrix_options.inverse = driver_settings.inverse
if driver_settings.rgb_sequence:
    matrix_options.led_rgb_sequence = driver_settings.rgb_sequence
if driver_settings.pwm_lsb_nanoseconds:
    matrix_options.pwm_lsb_nanoseconds = driver_settings.pwm_lsb_nanoseconds
if driver_settings.pwm_dither_bits:
    matrix_options.pwm_dither_bits = driver_settings.pwm_dither_bits
if driver_settings.no_hardware_pulse:
    matrix_options.disable_hardware_pulsing = driver_settings.no_hardware_pulse
if driver_settings.panel_type:
    matrix_options.panel_type = driver_settings.panel_type
if driver_settings.slowdown_gpio:
    matrix_options.gpio_slowdown = driver_settings.slowdown_gpio
if driver_settings.daemon:
    matrix_options.daemon = driver_settings.daemon
if driver_settings.no_drop_privs:
    matrix_options.drop_privileges = 1
