import cProfile
import uuid
from typing import Callable
from wideboy.config import settings


def get_unique_device_id(self):
    return uuid.UUID(int=uuid.getnode()).hex[-8:]


def main_entrypoint(main_func: Callable) -> None:
    if settings.general.profiling in ["ncalls", "tottime"]:
        cProfile.run("main_func()", None, sort=settings.general.profiling)
    else:
        main_func()
