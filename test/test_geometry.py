import pytest
import math

from geometry import dist, pdist, Point


class TestGeometry:
    def test_dist(self):
        assert dist(1, 2, 4, 6) == 5
        assert dist(8, 3, 7, 4) == pytest.approx(math.sqrt(2))

    def test_pdist(self):
        p1 = Point(1, 2)
        p2 = Point(4, 6)
        assert pdist(p1, p2) == 5

        p1 = Point(8, 3)
        p2 = Point(7, 4)
        assert pdist(p1, p2) == pytest.approx(math.sqrt(2))
