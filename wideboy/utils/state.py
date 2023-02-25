class StateStore:
    power: bool = True
    brightness: int = 255

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness})"


state = StateStore()
