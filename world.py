import random

from geometry import Direction, Point
from squirrel import Squirrel


class World:
    def __init__(self, map, N_GROUND_TILES=1):
        self.MAP = map
        self.WIDTH_TILES = len(self.MAP[0])
        self.HEIGHT_TILES = len(self.MAP)
        self.N_GROUND_TILES = N_GROUND_TILES

        self.GROUND_LAYER = [[{} for x in range(self.WIDTH_TILES)]
                             for y in range(self.HEIGHT_TILES)]

        for x in range(self.WIDTH_TILES):
            for y in range(self.HEIGHT_TILES):
                self.GROUND_LAYER[y][x]['tileidx'] = \
                    random.randint(0, self.N_GROUND_TILES-1)

        self.squirrel = Squirrel(Point(14, 14), Direction.DOWN)
        self.squirrels = []
        self.nuts = {}

    def random_point(self):
        x = random.randint(0, self.WIDTH_TILES - 1)
        y = random.randint(0, self.HEIGHT_TILES - 1)
        return Point(x, y)

    def can_move_to(self, pos):
        if pos.x < 0 or pos.x >= self.WIDTH_TILES or pos.y < 0 or pos.y >= self.HEIGHT_TILES:
            return False
        if pos == self.squirrel.pos:
            return False
        for squirrel in self.squirrels:
            if pos == squirrel.pos:
                return False
        for nut in self.nuts.values():
            if pos == nut.pos:
                return False
        return True
