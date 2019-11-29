import pytest

from geometry import Point
from npc import find_path_astar, successors
from world import World


class TestNPC:
    def test_successors(self):
        world = World([['x' for x in range(10)] for y in range(10)])
        ss = successors(world, Point(4, 5))
        assert ss == [Point(3, 4), Point(3, 5), Point(3, 6), Point(4, 4),
                      Point(4, 6), Point(5, 4), Point(5, 5), Point(5, 6)]

        ss = successors(world, Point(0, 0))
        assert ss == [Point(0, 1), Point(1, 0), Point(1, 1)]

        ss = successors(world, Point(9, 9))
        assert ss == [Point(8, 8), Point(8, 9), Point(9, 8)]

    def test_successors_impassable(self):
        map = [['x' for x in range(10)] for y in range(10)]
        map[6][3] = '#'
        map[6][4] = '#'
        world = World(map)
        ss = successors(world, Point(4, 5), '#')
        assert ss == [Point(3, 4), Point(3, 5), Point(4, 4),
                      Point(5, 4), Point(5, 5), Point(5, 6)]

    def test_find_path_astar(self):
        world = World([['x' for x in range(10)] for y in range(10)])
        path = find_path_astar(world, Point(1, 2), Point(7, 6))
        assert path == [Point(1, 2), Point(2, 3), Point(3, 4), Point(4, 5), Point(5, 6), Point(6, 6), Point(7, 6)]

    def test_find_path_astar_obstacles(self):
        world = World([
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
        ])
        path = find_path_astar(world, Point(7, 3), Point(4, 7), '#')
        assert path == [Point(7, 3), Point(6, 4), Point(5, 4), Point(4, 4), Point(3, 4), Point(2, 4), Point(1, 4),
                        Point(0, 5), Point(1, 6), Point(2, 7), Point(3, 7), Point(4, 7)]

    def test_find_path_astar_obstacles_2(self):
        world = World([
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
        ])
        path = find_path_astar(world, Point(9, 3), Point(0, 5), '#')
        assert path == [Point(9, 3), Point(9, 2), Point(8, 1), Point(7, 1), Point(6, 1), Point(5, 1), Point(4, 2),
                        Point(3, 3), Point(2, 4), Point(1, 4), Point(0, 5)]

    def test_find_path_astar_same_place(self):
        world = World([
            '..',
            '..',
        ])
        path = find_path_astar(world, Point(1, 0), Point(1, 0), '#')
        assert path == [Point(1, 0)]

    def test_find_path_astar_no_path(self):
        world = World([
            '.....',
            '.###.',
            '.#.#.',
            '.###.',
            '.....',
        ])
        path = find_path_astar(world, Point(2, 2), Point(4, 4), '#')
        assert path is None

    def test_find_path_astar_within(self):
        world = World([
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
        ])
        path = find_path_astar(world, Point(7, 3), Point(5, 7), '#', within=1)
        assert path == [Point(7, 3), Point(6, 4), Point(5, 4), Point(4, 4), Point(3, 4), Point(2, 4), Point(1, 4),
                        Point(0, 5), Point(1, 6), Point(2, 7), Point(3, 7), Point(4, 7)]
