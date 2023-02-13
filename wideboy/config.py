import os


def get_config_env_var(key, default=None):
    return os.environ.get(key, default)


FPS = int(get_config_env_var("FPS", 60))

CANVAS_WIDTH = int(get_config_env_var("CANVAS_WIDTH", 64 * 12))
CANVAS_HEIGHT = int(get_config_env_var("CANVAS_HEIGHT", 64 * 1))
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)

DEBUG = get_config_env_var("DEBUG", "false") == "true"
LOG_DEBUG = get_config_env_var("LOG_LEVEL", "info").lower() == "debug"
PROFILING = get_config_env_var("PROFILING", "")
