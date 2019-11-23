import enum
import random

from geometry import Direction, Rotation
from npc import NPC, find_path_astar


class Squirrel(NPC):
    __next_id = 1

    GET_NUT_PROBABILTY = 0.1

    class SquirrelState(enum.Enum):
        RANDOM = 1
        GETTING_NUT = 2

    def __init__(self, x, y, facing):
        self.id = Squirrel.__next_id
        Squirrel.__next_id += 1
        self.x = x
        self.y = y
        self.facing = facing
        self.energy = 1000
        self.state = Squirrel.SquirrelState.RANDOM
        self.target_nut_id = None

    def set_energy(self, energy):
        self.energy = min(1000, max(0, energy))

    def _randomly_target_nut(self, game):
        if self.state == Squirrel.SquirrelState.RANDOM and game.nuts:
            p = random.random()
            if p <= Squirrel.GET_NUT_PROBABILTY:
                self.state = Squirrel.SquirrelState.GETTING_NUT
                self.target_nut_id = list(game.nuts.keys())[random.randrange(0, len(game.nuts))]
                print(f"Squirrel {self.id} getting nut {self.target_nut_id}")

    def tick(self, game):
        self._randomly_target_nut(game)
        if self.state == Squirrel.SquirrelState.RANDOM:
            self.facing = Direction(random.randint(1, 4))
            newx, newy = game._move_in_direction(self.x, self.y, self.facing)
            if game._can_move_to(newx, newy):
                self.x, self.y = newx, newy
        elif self.state == Squirrel.SquirrelState.GETTING_NUT:
            target_nut = game.nuts.get(self.target_nut_id)
            if target_nut is not None:
                path = find_path_astar(game.MAP, self.x, self.y,
                                       target_nut.x, target_nut.y)
                if path is not None and len(path) > 1:
                    newx, newy = path[1]
                    if game._can_move_to(newx, newy):
                        self.x, self.y = newx, newy
                elif len(path) == 1:
                    del game.nuts[self.target_nut_id]
                    self.state = Squirrel.SquirrelState.RANDOM
                    print(f"Squrrel {self.id} ate nut {self.target_nut_id}")
                else:
                    print(f"Squrrel {self.id} failed to get nut {self.target_nut_id}: no path to nut")
                    self.state = Squirrel.SquirrelState.RANDOM
            else:
                print(f"Squrrel {self.id} failed to get nut {self.target_nut_id}: nut no longer exists")
                self.state = Squirrel.SquirrelState.RANDOM

