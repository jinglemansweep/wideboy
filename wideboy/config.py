import os
import sys


def get_config_env_var(key, default=None):
    return os.environ.get(key, default)


CANVAS_WIDTH = int(get_config_env_var("CANVAS_WIDTH", 64 * 12))
CANVAS_HEIGHT = int(get_config_env_var("CANVAS_HEIGHT", 64 * 1))
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)

MATRIX_ENABLED = get_config_env_var("MATRIX_ENABLED", "true") == "true"

MATRIX_WIDTH = int(get_config_env_var("MATRIX_WIDTH", 64 * 4))
MATRIX_HEIGHT = int(get_config_env_var("MATRIX_HEIGHT", 64 * 3))
MATRIX_SIZE = (MATRIX_WIDTH, MATRIX_HEIGHT)

MATRIX_PANEL_WIDTH = int(get_config_env_var("MATRIX_PANEL_WIDTH", 64))
MATRIX_PANEL_HEIGHT = int(get_config_env_var("MATRIX_PANEL_HEIGHT", 64))
MATRIX_PANEL_SIZE = (MATRIX_PANEL_WIDTH, MATRIX_PANEL_HEIGHT)

MQTT_HOST = get_config_env_var("MQTT_HOST", "hass.local")
MQTT_PORT = int(get_config_env_var("MQTT_PORT", 1883))
MQTT_USER = get_config_env_var("MQTT_USER", None)
MQTT_PASSWORD = get_config_env_var("MQTT_PASSWORD", None)

HASS_URL = get_config_env_var("HASS_URL", None)
HASS_API_TOKEN = get_config_env_var("HASS_API_TOKEN", None)

BACKGROUND_CHANGE_INTERVAL_MINS = int(
    get_config_env_var("BACKGROUND_CHANGE_INTERVAL_MINS", 5)
)

WEATHER_FETCH_INTERVAL = int(get_config_env_var("WEATHER_FETCH_INTERVAL", 600))
WEATHER_LATITUDE = float(get_config_env_var("WEATHER_LATITUDE", 52.0557))
WEATHER_LONGITUDE = float(get_config_env_var("WEATHER_LONGITUDE", 1.1153))

DEBUG = get_config_env_var("DEBUG", "false") == "true"
LOG_DEBUG = get_config_env_var("LOG_LEVEL", "info").lower() == "debug"
PROFILING = get_config_env_var("PROFILING", "")

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
if LED_ROWS:
    matrix_options.rows = LED_ROWS
if LED_COLS:
    matrix_options.cols = LED_COLS
if LED_CHAIN:
    matrix_options.chain_length = LED_CHAIN
if LED_PARALLEL:
    matrix_options.parallel = LED_PARALLEL
if LED_ROW_ADDR_TYPE:
    matrix_options.row_address_type = LED_ROW_ADDR_TYPE
if LED_MULTIPLEXING:
    matrix_options.multiplexing = LED_MULTIPLEXING
if LED_PIXEL_MAPPER:
    matrix_options.pixel_mapper_config = LED_PIXEL_MAPPER
if LED_PWM_BITS:
    matrix_options.pwm_bits = LED_PWM_BITS
if LED_BRIGHTNESS:
    matrix_options.brightness = LED_BRIGHTNESS
if LED_SCAN_MODE:
    matrix_options.scan_mode = LED_SCAN_MODE
if LED_ROW_ADDR_TYPE:
    matrix_options.row_addr_type = LED_ROW_ADDR_TYPE
if LED_SHOW_REFRESH:
    matrix_options.show_refresh_rate = LED_SHOW_REFRESH
if LED_LIMIT_REFRESH:
    matrix_options.limit_refresh_rate_hz = LED_LIMIT_REFRESH
if LED_INVERSE:
    matrix_options.inverse = LED_INVERSE
if LED_RGB_SEQUENCE:
    matrix_options.led_rgb_sequence = LED_RGB_SEQUENCE
if LED_PWM_LSB_NANOSECONDS:
    matrix_options.pwm_lsb_nanoseconds = LED_PWM_LSB_NANOSECONDS
if LED_PWM_DITHER_BITS:
    matrix_options.pwm_dither_bits = LED_PWM_DITHER_BITS
if LED_NO_HARDWARE_PULSE:
    matrix_options.disable_hardware_pulsing = 1
if LED_PANEL_TYPE:
    matrix_options.panel_type = LED_PANEL_TYPE
if LED_SLOWDOWN_GPIO:
    matrix_options.gpio_slowdown = LED_SLOWDOWN_GPIO
if LED_DAEMON:
    matrix_options.daemon = LED_DAEMON
if LED_NO_DROP_PRIVS:
    matrix_options.drop_privileges = 1
