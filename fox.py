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

    def __init__(self, game, pos, facing):
        super().__init__(game, pos, facing)
        self.id = Fox.__next_id
        Fox.__next_id += 1
        self.state = Fox.FoxState.RANDOM
        self.hunt_destination = None

    def _randomly_hunt(self):
        if self.state == Fox.FoxState.RANDOM and self.game.world.buried_nuts():
            buried_nuts = self.game.world.buried_nuts()
            p = random.random()
            if p <= Fox.HUNT_PROBABILITY:
                self.state = Fox.FoxState.HUNTING
                self.hunt_destination = \
                    buried_nuts[random.randrange(0, len(buried_nuts))].pos

    def _within_attack_range(self):
        d = pdist(self.pos, self.game.world.squirrel.pos)
        return d <= Fox.ATTACK_DISTANCE \
            and not self.game.world.is_tree(self.game.world.squirrel.pos)

    def tick(self):
        self._randomly_hunt()
        if self._within_attack_range():
            path = self.find_path_astar(self.game.world.squirrel.pos, 1)
            if path is not None and len(path) > 1:
                self.move_to(path[1])
                self.face_towards(self.game.world.squirrel.pos)
            elif path is not None and len(path) == 1:
                self.face_towards(self.game.world.squirrel.pos)
                self.game.over("You got eaten by a fox!")
        elif self.state == Fox.FoxState.RANDOM:
            self.move_randomly()
        elif self.state == Fox.FoxState.HUNTING:
            path = self.find_path_astar(self.hunt_destination)
            if path is not None and len(path) > 1:
                new_pos = path[1]
                if self.can_move_to(new_pos):
                    self.move_to(new_pos)
            else:
                self.state = Fox.FoxState.RANDOM

    @classmethod
    def _can_move_to(cls, game, pos):
        return not game.world.is_tree(pos)
