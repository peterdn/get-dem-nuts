import enum


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and \
            (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Rotation(enum.Enum):
    Clockwise = 1
    CounterClockwise = -1
