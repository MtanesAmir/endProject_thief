import pytest
from src.domain.distance import manhattan_distance, euclidean_distance, chebyshev_distance

def test_distance_metrics():
    p1 = (0, 0)
    p2 = (3, 4)
    assert manhattan_distance(p1, p2) == 7
    assert euclidean_distance(p1, p2) == pytest.approx(5.0)
    assert chebyshev_distance(p1, p2) == 4
