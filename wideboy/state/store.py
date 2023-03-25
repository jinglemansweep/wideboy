from typing import Optional


class StateStore:
    power: bool = True
    brightness: int = 128
    news_items: list[str] = []
    weather_summary: Optional[str] = None
    temperature: Optional[float] = None
    rain_probability: Optional[int] = None

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness} weather_summary={self.weather_summary} temp={self.temperature} rain_prob={self.rain_probability} news_items={self.news_items})"
