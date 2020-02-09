import random

from geometry import Direction, Point
from nut import Nut
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

        self.squirrel = Squirrel(Point(23, 22), Direction.DOWN)
        self.squirrels = []
        self.foxes = []
        self.nuts = {}

    def active_nuts(self):
        return list(filter(lambda nut: nut.state == Nut.NutState.ACTIVE,
                           self.nuts.values()))

    def buried_nuts(self):
        return list(filter(lambda nut: nut.state == Nut.NutState.BURIED,
                           self.nuts.values()))

    def random_point(self):
        x = random.randint(0, self.WIDTH_TILES - 1)
        y = random.randint(0, self.HEIGHT_TILES - 1)
        return Point(x, y)

    def in_world_bounds(self, pos):
        if pos.x < 0 or pos.x >= self.WIDTH_TILES or pos.y < 0 \
                or pos.y >= self.HEIGHT_TILES:
            return False
        return True

    def can_move_to(self, pos):
        if not self.in_world_bounds(pos):
            return False
        if pos == self.squirrel.pos:
            return False
        for squirrel in self.squirrels:
            if pos == squirrel.pos:
                return False
        for nut in self.nuts.values():
            if nut.state == Nut.NutState.ACTIVE and pos == nut.pos:
                return False
        return True

    def is_tree(self, pos):
        return self.in_world_bounds(pos) and self.MAP[pos.y][pos.x] == '#'

    def is_nut(self, pos):
        if not self.in_world_bounds(pos):
            return None
        for nut in self.nuts.values():
            if nut.pos.x == pos.x and nut.pos.y == pos.y:
                return nut
        return None

    def is_npc(self, pos):
        for squirrel in self.squirrels:
            if pos == squirrel.pos:
                return True

        for fox in self.foxes:
            if pos == fox.pos:
                return True

        return False

    def can_bury_nut(self, pos):
        if self.is_tree(pos) or self.is_nut(pos):
            return False
        if self.is_npc(pos):
            return False
        return self.in_world_bounds(pos)
