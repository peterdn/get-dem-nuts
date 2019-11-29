import enum
import random

from geometry import pdist
from npc import NPC


class Fox(NPC):
    ATTACK_DISTANCE = 8

    __next_id = 1

    class FoxState(enum.Enum):
        RANDOM = 1
        LURKING = 2
        CHASING = 3

    def __init__(self, pos, facing):
        super().__init__(pos, facing)
        self.id = Fox.__next_id
        Fox.__next_id += 1
        self.state = Fox.FoxState.RANDOM

    def tick(self, game):
        if pdist(self.pos, game.world.squirrel.pos) <= Fox.ATTACK_DISTANCE \
                and not game.world.is_tree(game.world.squirrel.pos):
            path = self.find_path_astar(game.world, game.world.squirrel.pos, 1)
            if path is not None and len(path) > 1:
                self.move_to(path[1])
                self.face_towards(game.world.squirrel.pos)
            elif path is not None and len(path) == 1:
                self.face_towards(game.world.squirrel.pos)
                game.over("You got eaten by a fox!")
        elif self.state == Fox.FoxState.RANDOM:
            self.move_randomly(game)

    @classmethod
    def _can_move_to(cls, world, pos):
        return not world.is_tree(pos)
