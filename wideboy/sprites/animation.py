import enum
from typing import Tuple

# ANIMATION HELPERS


class AnimatorState(enum.Enum):
    OPEN = 1
    CLOSED = 2
    OPENING = 3
    CLOSING = 4


class Animator:
    def __init__(self, range: Tuple[float, float], open=True, speed=1.0) -> None:
        self.range = range
        self.speed = speed
        self.open = open
        self.value = range[1] if open else range[0]

    @property
    def state(self) -> AnimatorState:
        if self.open:
            return (
                AnimatorState.OPEN
                if self.value == self.range[1]
                else AnimatorState.OPENING
            )
        else:
            return (
                AnimatorState.CLOSED
                if self.value == self.range[0]
                else AnimatorState.CLOSING
            )

    @property
    def animating(self) -> bool:
        return self.value != self.range[0] and self.value != self.range[1]

    def toggle(self) -> None:
        self.open = not self.open

    def set(self, open: bool) -> None:
        self.open = open

    def update(self) -> None:
        value = self.value + self.speed if self.open else self.value - self.speed
        if value > self.range[1]:
            value = self.range[1]
        elif value < self.range[0]:
            value = self.range[0]
        self.value = value

    def __repr__(self) -> str:
        return f"Animator(value={self.value}, open={self.open}, state={self.state}, range={self.range}, speed={self.speed})"
