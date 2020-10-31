import random

from astar import find_path_astar
from character import Character
from geometry import Direction, Point


class NPC(Character):
    def __init__(self, game, pos, facing):
        super().__init__(game, pos, facing)

    def move_randomly(self):
        self.facing = Direction(random.randint(1, 4))
        new_pos = self.game._move_in_direction(self.pos, self.facing)
        if self.can_move_to(new_pos):
            self.pos = new_pos

    def find_path_astar(self, dst, within=0):
        return find_path_astar(self.game.world.MAP, self.pos, dst, self,
                               within)
