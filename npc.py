from abc import ABC, abstractclassmethod
import math
from queue import PriorityQueue
import random

from astar import find_path_astar
from geometry import Direction, pdist, Point


class Character(ABC):
    def __init__(self, pos, facing):
        self.pos = pos
        self.facing = facing

    def move_to(self, dst):
        self.face_towards(dst)
        self.pos = dst

    def face_towards(self, dst):
        if dst.y > self.pos.y:
            self.facing = Direction.DOWN
        elif dst.y < self.pos.y:
            self.facing = Direction.UP
        elif dst.x > self.pos.x:
            self.facing = Direction.RIGHT
        elif dst.x < self.pos.x:
            self.facing = Direction.LEFT

    @abstractclassmethod
    def _can_move_to(cls, world, pos):
        pass

    def can_move_to(self, world, pos):
        if not world.can_move_to(pos):
            return False
        return self._can_move_to(world, pos)

    def find_path_astar(self, world, dst, within=0):
        return find_path_astar(world, self.pos, dst, self, within)


class NPC(Character):
    def __init__(self, pos, facing):
        super().__init__(pos, facing)

    def move_randomly(self, game):
        self.facing = Direction(random.randint(1, 4))
        new_pos = game._move_in_direction(self.pos, self.facing)
        if self.can_move_to(game.world, new_pos):
            self.pos = new_pos
