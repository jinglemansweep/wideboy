from typing import Optional


class StateStore:
    power: bool = True
    brightness: int = 255
    news_items: list[str] = ([],)
    temperature: Optional[float] = None
    rain_probability: Optional[int] = None

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness} temp={self.temperature} rain_prob={self.rain_probability} news_items={self.news_items})"


state = StateStore()
