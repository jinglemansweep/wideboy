from typing import Optional


class StateStore:
    power: bool = True
    brightness: int = 128
    notifications: list[str] = list()
    weather_summary: Optional[str] = None
    temperature: Optional[float] = None
    rain_probability: Optional[int] = None

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness} notifications={len(self.notifications)} weather_summary={self.weather_summary} temp={self.temperature} rain_prob={self.rain_probability})"
