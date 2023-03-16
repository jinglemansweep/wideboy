import uuid


def get_device_id() -> str:
    return uuid.UUID(int=uuid.getnode()).hex[-8:]


DEVICE_ID = get_device_id()
