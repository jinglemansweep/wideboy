import pytweening
import time

pos = [0.0, 0.0]
vel = [0.001, 0.001]
x = 0.0
dir = 1


class Sprite:
    def __init__(self, position: tuple[int, int]):
        self.position = (float(position[0]), float(position[1]))
        self.log()

    def move(self, position: tuple[float, float]):
        self.position = position
        self.log()

    def log(self):
        print(f"sprite x={self.position[0]} y={self.position[1]}")


class Mover:
    def __init__(self, sprite, tweener, start, finish, length=100, delay=0.01):
        self.sprite = sprite
        self.tweener = tweener
        self.start = start
        self.finish = finish
        self.length = length
        self.delay = delay
        self.distances = (
            abs(self.finish[0] - self.start[0]),
            abs(self.finish[1] - self.start[1]),
        )
        self.steps = (self.distances[0] / length, self.distances[1] / length)
        self.index = 0
        print(
            f"mover start={self.start} finish={self.finish} length={self.length} distances={self.distances} steps={self.steps}"
        )

    def run(self):
        for i in range(self.length):
            ri = i / self.length
            tv = self.tweener(ri)
            x = self.start[0] + (self.distances[0] * tv)
            y = self.start[1] + (self.distances[1] * tv)
            self.sprite.move((x, y))
            time.sleep(self.delay)


sprite = Sprite((0.0, 0.0))
mover = Mover(sprite, pytweening.easeInOutSine, (0, 0), (120, 50), 100)

mover.run()

"""
while True:
    val = pytweening.easeInOutSine(x)

    x += dir * vel[0]
    if x >= 1.0:
        x = 1.0
        dir = -1
    if x <= 0:
        x = 0.0
        dir = 1
    time.sleep(0.001)
"""
