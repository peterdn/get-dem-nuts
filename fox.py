import enum
import random

from npc import NPC


class Fox(NPC):
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
        if self.state == Fox.FoxState.RANDOM:
            self.move_randomly(game)

    @classmethod
    def _can_move_to(cls, world, pos):
        return not world.is_tree(pos)
