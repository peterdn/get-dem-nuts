import enum
import random

from geometry import Direction, Rotation
from npc import NPC, find_path_astar
from nut import Nut


class Squirrel(NPC):
    __next_id = 1

    GET_NUT_PROBABILTY = 0.1

    class SquirrelState(enum.Enum):
        RANDOM = 1
        GETTING_NUT = 2

    def __init__(self, pos, facing):
        super().__init__(pos, facing)
        self.id = Squirrel.__next_id
        Squirrel.__next_id += 1
        self.energy = 1000
        self.state = Squirrel.SquirrelState.RANDOM
        self.target_nut_id = None
        self.carrying_nut = None

    def set_energy(self, energy):
        self.energy = min(1000, max(0, energy))

    def _randomly_target_nut(self, game):
        if self.state == Squirrel.SquirrelState.RANDOM \
                and game.world.active_nuts():
            active_nuts = game.world.active_nuts()
            p = random.random()
            if p <= Squirrel.GET_NUT_PROBABILTY:
                self.state = Squirrel.SquirrelState.GETTING_NUT
                self.target_nut_id = \
                    active_nuts[random.randrange(0, len(active_nuts))].id

    def tick(self, game):
        self._randomly_target_nut(game)
        if self.state == Squirrel.SquirrelState.RANDOM:
            self.move_randomly(game)
        elif self.state == Squirrel.SquirrelState.GETTING_NUT:
            target_nut = game.world.nuts.get(self.target_nut_id)
            if target_nut is not None \
                    and target_nut.state == Nut.NutState.ACTIVE:
                path = self.find_path_astar(game.world, target_nut.pos,
                                            within=1)
                if path is not None and len(path) > 1:
                    new_pos = path[1]
                    if self.can_move_to(game.world, new_pos):
                        self.move_to(new_pos)
                elif path is not None and len(path) == 1:
                    self.face_towards(target_nut.pos)
                    del game.world.nuts[self.target_nut_id]
                    self.state = Squirrel.SquirrelState.RANDOM
                else:
                    self.state = Squirrel.SquirrelState.RANDOM
            else:
                self.state = Squirrel.SquirrelState.RANDOM

    def is_carrying_nut(self):
        return self.carrying_nut is not None

    @classmethod
    def _can_move_to(cls, world, pos):
        return True
