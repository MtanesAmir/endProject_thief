import pytest
from src.domain.barriers import BarrierManager

def test_barrier_manager():
    bm = BarrierManager(max_barriers=14, grid_size=7)
    assert bm.count() == 0
    assert bm.add_barrier((2, 2)) is True
    assert bm.is_blocked((2, 2)) is True
    assert bm.is_blocked((0, 0)) is False
    assert bm.count() == 1
    bm.clear()
    assert bm.count() == 0
