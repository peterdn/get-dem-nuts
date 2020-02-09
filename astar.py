from queue import PriorityQueue

from geometry import pdist, Point


def successors(world, src, impassable=None):
    if impassable is None:
        impassable = ''

    height = len(world.MAP)
    width = len(world.MAP[0])

    def valid_successor(p):
        if p.x == src.x and p.y == src.y:
            return False
        if p.x < 0 or p.y < 0 or p.x >= width or p.y >= height:
            return False

        if isinstance(impassable, str):
            return world.MAP[p.y][p.x] not in impassable
        elif isinstance(impassable, object):
            return impassable.can_move_to(world, p)

    successors = [Point(x, y) for x in range(src.x-1, src.x+2)
                  for y in range(src.y-1, src.y+2)]

    successors = list(filter(valid_successor, successors))
    return successors


def visit(visited, pos, parent=None):
    visited[pos.y][pos.x] = {}
    visited[pos.y][pos.x]['cost'] = 0
    visited[pos.y][pos.x]['parent'] = parent
    if parent is not None:
        visited[pos.y][pos.x]['cost'] = visited[parent.y][parent.x]['cost'] + \
            pdist(parent, pos)


def reconstruct_path(visited, src, dst):
    pos = Point(dst.x, dst.y)
    path = [pos]
    while pos != src:
        pos = visited[pos.y][pos.x]['parent']
        path.append(pos)
    path.reverse()
    return path


def find_path_astar(world, src, dst, impassable=None, within=0):
    if impassable is None:
        impassable = ''

    visited = [[False for x in range(world.WIDTH_TILES)]
               for y in range(world.HEIGHT_TILES)]
    visit(visited, src)
    fringe = PriorityQueue()
    fringe.put((0, src))
    while not fringe.empty():
        (_priority, pos) = fringe.get()
        if pdist(pos, dst) <= within:
            break
        succs = successors(world, pos, impassable)
        for succ in succs:
            if not visited[succ.y][succ.x]:
                visit(visited, succ, pos)
                hcost = visited[succ.y][succ.x]['cost'] + \
                    pdist(succ, dst)
                fringe.put((hcost, succ))
    if pdist(pos, dst) <= within:
        return reconstruct_path(visited, src, pos)
    else:
        return None
