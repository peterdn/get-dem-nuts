import random

from geometry import Point


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

    def random_point(self):
        x = random.randint(0, self.WIDTH_TILES - 1)
        y = random.randint(0, self.HEIGHT_TILES - 1)
        return Point(x, y)
