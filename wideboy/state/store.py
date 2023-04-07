from typing import Optional


class StateStore:
    power: bool = True
    brightness: int = 128
    notifications: list[str] = list()

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness} notifications={len(self.notifications)})"
