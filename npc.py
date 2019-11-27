from abc import ABC
import functools
import math
from queue import PriorityQueue

from geometry import Direction, dist, Point

sign = functools.partial(math.copysign, 1)


class Character(ABC):
    def __init__(self):
        pass

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


class NPC(Character):
    def __init__(self):
        pass


def successors(map, src, impassable=None):
    if impassable is None:
        impassable = ''

    height = len(map)
    width = len(map[0])

    def valid_successor(p):
        if p.x == src.x and p.y == src.y:
            return False
        if p.x < 0 or p.y < 0 or p.x >= width or p.y >= height:
            return False
        return map[p.y][p.x] not in impassable

    successors = [Point(x, y) for x in range(src.x-1, src.x+2)
                  for y in range(src.y-1, src.y+2)]

    successors = list(filter(valid_successor, successors))
    return successors


def visit(visited, pos, parent=None):
    visited[pos.y][pos.x] = {}
    visited[pos.y][pos.x]['cost'] = 0
    visited[pos.y][pos.x]['parent'] = parent
    if parent is not None:
        visited[pos.y][pos.x]['cost'] = visited[parent.y][parent.x]['cost'] + 1


def reconstruct_path(visited, src, dst):
    pos = Point(dst.x, dst.y)
    path = [pos]
    while pos != src:
        pos = visited[pos.y][pos.x]['parent']
        path.append(pos)
    path.reverse()
    return path


def find_path_astar(world, src, dst, impassable=None):
    if impassable is None:
        impassable = ''

    visited = [[False for x in range(world.WIDTH_TILES)]
               for y in range(world.HEIGHT_TILES)]
    visit(visited, src)
    fringe = PriorityQueue()
    fringe.put((0, src))
    while not fringe.empty():
        (_priority, pos) = fringe.get()
        if pos == dst:
            break
        succs = successors(world.MAP, pos, impassable)
        for succ in succs:
            if not visited[succ.y][succ.x]:
                visit(visited, succ, pos)
                hcost = visited[succ.y][succ.x]['cost'] + dist(succ.x, succ.y, dst.x, dst.y)
                fringe.put((hcost, succ))
    if pos == dst:
        return reconstruct_path(visited, src, dst)
    else:
        return None
