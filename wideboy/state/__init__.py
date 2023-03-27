from wideboy.state.store import StateStore
from wideboy.utils.helpers import get_device_id
from wideboy.config import settings

STATE = StateStore()
DEVICE_ID = settings.general.device_id or get_device_id()
