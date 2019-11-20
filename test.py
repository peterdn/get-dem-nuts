import pytest

from npc import find_path


class TestNPC:
    def test_find_path_vertical_line_increasing(self):
        fromx, fromy = 10, 4
        tox, toy = 10, 15
        path = find_path(fromx, fromy, tox, toy)
        assert path == [
            (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10),
            (10, 11), (10, 12), (10, 13), (10, 14), (10, 15)]

    def test_find_path_vertical_line_decreasing(self):
        fromx, fromy = 10, 15
        tox, toy = 10, 4
        path = find_path(fromx, fromy, tox, toy)
        assert path == [
            (10, 15), (10, 14), (10, 13), (10, 12), (10, 11), (10, 10), (10, 9),
            (10, 8), (10, 7), (10, 6), (10, 5), (10, 4)]

    def test_find_path_same_place(self):
        fromx, fromy = 8, 10
        tox, toy = 8, 10
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(8, 10)]

    def test_find_path_diagonal_positive_gradient(self):
        fromx, fromy = 4, 5
        tox, toy = 8, 9
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]

    def test_find_path_diagonal_negative_gradient(self):
        fromx, fromy = 4, 15
        tox, toy = 8, 11
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(4, 15), (5, 14), (6, 13), (7, 12), (8, 11)]

    def test_find_path_positive_gradient(self):
        fromx, fromy = 4, 5
        tox, toy = 8, 17
        path = find_path(fromx, fromy, tox, toy)
        assert path == \
            [(4, 5), (4, 6), (5, 7), (5, 8), (5, 9), (6, 10),
             (6, 11), (6, 12), (7, 13), (7, 14), (7, 15), (8, 16), (8, 17)]

    def test_find_path_negative_gradient(self):
        fromx, fromy = 4, 15
        tox, toy = 9, 13
        path = find_path(fromx, fromy, tox, toy)
        assert path == \
            [(4, 15), (5, 15), (6, 14), (7, 14), (8, 13), (9, 13)]

    def test_find_path_negative_gradient_2(self):
        fromx, fromy = 13, 2
        tox, toy = 5, 12
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(13, 2), (12, 3), (11, 4), (11, 5), (10, 6), (9, 7),
                        (8, 8), (7, 9), (7, 10), (6, 11), (5, 12)]

    def test_find_path_negative_gradient_3(self):
        fromx, fromy = 13, 13
        tox, toy = 6, 7
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(13, 13), (12, 12), (11, 11), (10, 10), (9, 10),
                        (8, 9), (7, 8), (6, 7)]

    def test_find_path_negative_gradient_4(self):
        fromx, fromy = 13, 13
        tox, toy = 6, 4
        path = find_path(fromx, fromy, tox, toy)
        assert path == [(13, 13), (12, 12), (11, 11), (11, 10), (10, 9),
                        (9, 8), (8, 7), (8, 6), (7, 5), (6, 4)]
