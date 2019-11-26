import random

from map import MAP


class World:
    def __init__(self, N_GROUND_TILES):
        self.MAP = MAP
        self.WIDTH_TILES = len(self.MAP[0])
        self.HEIGHT_TILES = len(self.MAP)
        self.N_GROUND_TILES = N_GROUND_TILES

        self.GROUND_LAYER = [[{} for x in range(self.WIDTH_TILES)]
                             for y in range(self.HEIGHT_TILES)]

        for x in range(self.WIDTH_TILES):
            for y in range(self.HEIGHT_TILES):
                self.GROUND_LAYER[y][x]['tileidx'] = \
                    random.randint(0, self.N_GROUND_TILES-1)
