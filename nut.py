import enum

from geometry import Point


class Nut:
    __next_id = 1

    class NutState(enum.Enum):
        ACTIVE = 1
        BURIED = 2

    def __init__(self, x, y, state=NutState.ACTIVE):
        self.state = state
        self.pos = Point(x, y)
        self.id = Nut.__next_id
        Nut.__next_id += 1
        self.energy = 250
