import pytest

from geometry import Point
from npc import find_path_astar, successors


class TestNPC:
    def test_successors(self):
        map = [['x' for x in range(10)] for y in range(10)]
        ss = successors(map, Point(4, 5))
        assert ss == [Point(3, 4), Point(3, 5), Point(3, 6), Point(4, 4),
                      Point(4, 6), Point(5, 4), Point(5, 5), Point(5, 6)]

        ss = successors(map, Point(0, 0))
        assert ss == [Point(0, 1), Point(1, 0), Point(1, 1)]

        ss = successors(map, Point(9, 9))
        assert ss == [Point(8, 8), Point(8, 9), Point(9, 8)]

    def test_successors_impassable(self):
        map = [['x' for x in range(10)] for y in range(10)]
        map[6][3] = '#'
        map[6][4] = '#'
        ss = successors(map, Point(4, 5), '#')
        assert ss == [Point(3, 4), Point(3, 5), Point(4, 4),
                      Point(5, 4), Point(5, 5), Point(5, 6)]

    def test_find_path_astar(self):
        map = [['x' for x in range(10)] for y in range(10)]
        path = find_path_astar(map, Point(1, 2), Point(7, 6))
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
        path = find_path_astar(map, Point(7, 3), Point(4, 7), '#')
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
        path = find_path_astar(map, Point(9, 3), Point(0, 5), '#')
        assert path == [(9, 3), (9, 2), (8, 1), (7, 1), (6, 1), (5, 1), (4, 2),
                        (3, 3), (2, 4), (1, 4), (0, 5)]

    def test_find_path_astar_same_place(self):
        map = [
            '..',
            '..',
        ]
        path = find_path_astar(map, Point(1, 0), Point(1, 0), '#')
        assert path == [(1, 0)]

    def test_find_path_astar_no_path(self):
        map = [
            '.....',
            '.###.',
            '.#.#.',
            '.###.',
            '.....',
        ]
        path = find_path_astar(map, Point(2, 2), Point(4, 4), '#')
        assert path is None
