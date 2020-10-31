from dataclasses import dataclass
from queue import PriorityQueue
from typing import List, Optional, Tuple, Union

from character import Character
from geometry import pdist, Point


def successors(world_map: List[str],
               src: Point,
               impassable: Optional[Union[str, Character]] = None):

    if impassable is None:
        impassable = ''

    height = len(world_map)
    width = len(world_map[0])

    def valid_successor(p: Point):
        if p.x == src.x and p.y == src.y:
            return False
        if p.x < 0 or p.y < 0 or p.x >= width or p.y >= height:
            return False

        if isinstance(impassable, str):
            return world_map[p.y][p.x] not in impassable
        elif isinstance(impassable, Character):
            return impassable.can_move_to(p)

    successors = [Point(x, y) for x in range(src.x-1, src.x+2)
                  for y in range(src.y-1, src.y+2)]

    successors = list(filter(valid_successor, successors))
    return successors


@dataclass
class VisitState:
    visited: bool = False
    cost: float = 0
    parent: Optional[Point] = None


def visit(visited: List[List[VisitState]],
          pos: Point,
          parent: Optional[Point] = None):
    visited[pos.y][pos.x] = VisitState(True, 0, parent)
    if parent is not None:
        visited[pos.y][pos.x].cost = visited[parent.y][parent.x].cost + \
            pdist(parent, pos)


def reconstruct_path(visited: List[List[VisitState]],
                     src: Point,
                     dst: Point):
    pos = Point(dst.x, dst.y)
    path = [pos]
    while pos != src:
        parent = visited[pos.y][pos.x].parent
        assert parent is not None
        pos = parent
        path.append(pos)
    path.reverse()
    return path


def find_path_astar(world_map: List[str],
                    src: Point,
                    dst: Point,
                    impassable: Optional[Union[str, Character]] = None,
                    within: int = 0):

    if impassable is None:
        impassable = ''

    visited = [[VisitState() for x in range(len(world_map[0]))]
               for y in range(len(world_map))]
    visit(visited, src)
    fringe: PriorityQueue[Tuple[int, Point]] = PriorityQueue()
    fringe.put((0, src))
    while not fringe.empty():
        (_, pos) = fringe.get()
        if pdist(pos, dst) <= within:
            break
        succs = successors(world_map, pos, impassable)
        for succ in succs:
            if not visited[succ.y][succ.x].visited:
                visit(visited, succ, pos)
                hcost = visited[succ.y][succ.x].cost + \
                    pdist(succ, dst)
                fringe.put((hcost, succ))
    if pdist(pos, dst) <= within:
        return reconstruct_path(visited, src, pos)
    else:
        return None
