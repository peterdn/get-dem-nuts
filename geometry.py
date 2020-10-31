from dataclasses import dataclass
import enum
import math


def _dist(x: int, y: int, tx: int, ty: int) -> float:
    return math.sqrt((x - tx)**2 + (y - ty)**2)


@dataclass(order=True, frozen=True)
class Point:
    x: int
    y: int


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
