import enum
import math


def _dist(x: int, y: int, tx: int, ty: int) -> float:
    return math.sqrt((x - tx)**2 + (y - ty)**2)


class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other) -> bool:
        return isinstance(other, Point) and \
            (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __lt__(self, other) -> bool:
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            raise NotImplementedError


def pdist(p1: Point, p2: Point) -> float:
    return _dist(p1.x, p1.y, p2.x, p2.y)


class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Rotation(enum.Enum):
    Clockwise = 1
    CounterClockwise = -1
