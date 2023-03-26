from typing import Optional


class StateStore:
    power: bool = True
    brightness: int = 128
    scene: Optional[str] = None
    news_items: list[str] = []
    weather_summary: Optional[str] = None
    temperature: Optional[float] = None
    rain_probability: Optional[int] = None

    def __str__(self):
        return f"State(power={self.power} brightness={self.brightness} scene={self.scene} weather_summary={self.weather_summary} temp={self.temperature} rain_prob={self.rain_probability} news_items={self.news_items})"

    def set_led_power(self, state: bool) -> None:
        self.power = state

    def set_led_brightness(self, brightness: int) -> None:
        self.brightness = brightness

    def set_scene(self, scene: str) -> None:
        self.scene = scene

    def set_weather(
        self, summary: str, temperature: float, rain_probability: int
    ) -> None:
        self.weather_summary = summary
        self.temperature = temperature
        self.rain_probability = rain_probability
