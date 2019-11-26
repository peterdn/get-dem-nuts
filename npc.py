from abc import ABC
import functools
import math
from queue import PriorityQueue

from geometry import Point

sign = functools.partial(math.copysign, 1)


class NPC(ABC):
    def __init__(self):
        self.x = 0
        self.y = 0


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


def visit(visited, x, y, parentx=None, parenty=None):
    visited[y][x] = {}
    visited[y][x]['cost'] = 0
    visited[y][x]['parent'] = (parentx, parenty)
    if parentx is not None and parenty is not None:
        visited[y][x]['cost'] = visited[parenty][parentx]['cost'] + 1


def dist(x, y, tx, ty):
    return math.sqrt((x - tx)**2 + (y - ty)**2)


def reconstruct_path(visited, fromx, fromy, tox, toy):
    (cx, cy) = (tox, toy)
    path = [(cx, cy)]
    while (cx, cy) != (fromx, fromy):
        (cx, cy) = visited[cy][cx]['parent']
        path.append((cx, cy))
    path.reverse()
    return path


def find_path_astar(map, src, dst, impassable=None):
    if impassable is None:
        impassable = ''

    height = len(map)
    width = len(map[0])

    visited = [[False for x in range(width)] for y in range(height)]
    visit(visited, src.x, src.y)
    fringe = PriorityQueue()
    fringe.put((0, (src.x, src.y)))
    while not fringe.empty():
        (p, (cx, cy)) = fringe.get()
        if (cx, cy) == (dst.x, dst.y):
            break
        succs = successors(map, Point(cx, cy), impassable)
        for succ in succs:
            if not visited[succ.y][succ.x]:
                visit(visited, succ.x, succ.y, cx, cy)
                hcost = visited[succ.y][succ.x]['cost'] + dist(succ.x, succ.y, dst.x, dst.y)
                fringe.put((hcost, (succ.x, succ.y)))
    if (cx, cy) == (dst.x, dst.y):
        return reconstruct_path(visited, src.x, src.y, dst.x, dst.y)
    else:
        return None
