from abc import ABC
import functools
import math
from queue import PriorityQueue

sign = functools.partial(math.copysign, 1)


class NPC(ABC):
    def __init__(self):
        self.x = 0
        self.y = 0


def successors(map, x, y, impassable=None):
    if impassable is None:
        impassable = ''

    height = len(map)
    width = len(map[0])

    def valid_successor(p):
        (px, py) = p
        if px == x and py == y:
            return False
        if px < 0 or py < 0 or px >= width or py >= height:
            return False
        return map[py][px] not in impassable

    successors = [(sx, sy) for sx in range(x-1, x+2)
                  for sy in range(y-1, y+2)]

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


def find_path_astar(map, fromx, fromy, tox, toy, impassable=None):
    if impassable is None:
        impassable = ''

    height = len(map)
    width = len(map[0])

    visited = [[False for x in range(width)] for y in range(height)]
    visit(visited, fromx, fromy)
    fringe = PriorityQueue()
    fringe.put((0, (fromx, fromy)))
    while not fringe.empty():
        (p, (cx, cy)) = fringe.get()
        if (cx, cy) == (tox, toy):
            break
        ss = successors(map, cx, cy, impassable)
        for (sx, sy) in ss:
            if not visited[sy][sx]:
                visit(visited, sx, sy, cx, cy)
                hcost = visited[sy][sx]['cost'] + dist(sx, sy, tox, toy)
                fringe.put((hcost, (sx, sy)))
    if (cx, cy) == (tox, toy):
        return reconstruct_path(visited, fromx, fromy, tox, toy)
    else:
        return None
