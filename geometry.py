import enum
import math


def _dist(x, y, tx, ty):
    return math.sqrt((x - tx)**2 + (y - ty)**2)


def pdist(p1, p2):
    return _dist(p1.x, p1.y, p2.x, p2.y)


class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        object.__setattr__(self, 'x', x)
        object.__setattr__(self, 'y', y)

    def __eq__(self, other):
        return isinstance(other, Point) and \
            (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __setattr__(self, *args):
        raise NotImplementedError


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Rotation(enum.Enum):
    Clockwise = 1
    CounterClockwise = -1
