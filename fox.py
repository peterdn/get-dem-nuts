import enum
import random

from geometry import pdist
from npc import NPC


class Fox(NPC):
    ATTACK_DISTANCE = 8
    HUNT_PROBABILITY = 0.01

    __next_id = 1

    class FoxState(enum.Enum):
        RANDOM = 1
        HUNTING = 2

    def __init__(self, pos, facing):
        super().__init__(pos, facing)
        self.id = Fox.__next_id
        Fox.__next_id += 1
        self.state = Fox.FoxState.RANDOM
        self.hunt_destination = None

    def _randomly_hunt(self, game):
        if self.state == Fox.FoxState.RANDOM and game.world.buried_nuts():
            buried_nuts = game.world.buried_nuts()
            p = random.random()
            if p <= Fox.HUNT_PROBABILITY:
                self.state = Fox.FoxState.HUNTING
                self.hunt_destination = buried_nuts[random.randrange(0, len(buried_nuts))].pos

    def _within_attack_range(self, game):
        return pdist(self.pos, game.world.squirrel.pos) <= Fox.ATTACK_DISTANCE \
                     and not game.world.is_tree(game.world.squirrel.pos)

    def tick(self, game):
        self._randomly_hunt(game)
        if self._within_attack_range(game):
            path = self.find_path_astar(game.world, game.world.squirrel.pos, 1)
            if path is not None and len(path) > 1:
                self.move_to(path[1])
                self.face_towards(game.world.squirrel.pos)
            elif path is not None and len(path) == 1:
                self.face_towards(game.world.squirrel.pos)
        elif self.state == Fox.FoxState.RANDOM:
            self.move_randomly(game)
        elif self.state == Fox.FoxState.HUNTING:
            path = self.find_path_astar(game.world, self.hunt_destination)
            if path is not None and len(path) > 1:
                new_pos = path[1]
                if self.can_move_to(game.world, new_pos):
                    self.move_to(new_pos)
            else:
                self.state = Fox.FoxState.RANDOM

    @classmethod
    def _can_move_to(cls, world, pos):
        return not world.is_tree(pos)
