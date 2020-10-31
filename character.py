from abc import ABC, abstractclassmethod

from geometry import Direction, Point


class Character(ABC):
    def __init__(self, game, pos, facing):
        self.game = game
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
    def _can_move_to(cls, pos):
        pass

    def can_move_to(self, pos):
        if not self.game.world.can_move_to(pos):
            return False
        return self._can_move_to(self.game, pos)
