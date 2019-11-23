import pytest

from npc import find_path_astar, successors


class TestNPC:
    def test_successors(self):
        map = [['x' for x in range(10)] for y in range(10)]
        ss = successors(map, 4, 5)
        assert ss == [(3, 4), (3, 5), (3, 6), (4, 4),
                      (4, 6), (5, 4), (5, 5), (5, 6)]

        ss = successors(map, 0, 0)
        assert ss == [(0, 1), (1, 0), (1, 1)]

        ss = successors(map, 9, 9)
        assert ss == [(8, 8), (8, 9), (9, 8)]

    def test_successors_impassable(self):
        map = [['x' for x in range(10)] for y in range(10)]
        map[6][3] = '#'
        map[6][4] = '#'
        ss = successors(map, 4, 5, '#')
        assert ss == [(3, 4), (3, 5), (4, 4),
                      (5, 4), (5, 5), (5, 6)]

    def test_find_path_astar(self):
        map = [['x' for x in range(10)] for y in range(10)]
        path = find_path_astar(map, 1, 2, 7, 6)
        assert path == [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 6), (7, 6)]

    def test_find_path_astar_obstacles(self):
        map = [
            '..........',
            '..........',
            '.....####.',
            '........#.',
            '........#.',
            '.########.',
            '.....#....',
            '.....#....',
            '.....#....',
            '..........',
            '..........',
        ]
        path = find_path_astar(map, 7, 3, 4, 7, '#')
        assert path == [(7, 3), (6, 4), (5, 4), (4, 4), (3, 4), (2, 4), (1, 4),
                        (0, 5), (1, 6), (2, 7), (3, 7), (4, 7)]

    def test_find_path_astar_obstacles_2(self):
        map = [
            '..........',
            '..........',
            '.....####.',
            '........#.',
            '........#.',
            '.########.',
            '.....#....',
            '.....#....',
            '.....#....',
            '..........',
            '..........',
        ]
        path = find_path_astar(map, 9, 3, 0, 5, '#')
        assert path == [(9, 3), (9, 2), (8, 1), (7, 1), (6, 1), (5, 1), (4, 2),
                        (3, 3), (2, 4), (1, 4), (0, 5)]

    def test_find_path_astar_same_place(self):
        map = [
            '..',
            '..',
        ]
        path = find_path_astar(map, 1, 0, 1, 0, '#')
        assert path == [(1, 0)]

    def test_find_path_astar_no_path(self):
        map = [
            '.....',
            '.###.',
            '.#.#.',
            '.###.',
            '.....',
        ]
        path = find_path_astar(map, 2, 2, 4, 4, '#')
        assert path is None
