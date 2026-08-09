import pytest
from src.strategy.police_brain import MyPoliceBrain

def test_police_brain():
    pb = MyPoliceBrain((0, 0), 7)
    move1 = pb._pick_move({"thief_pos": (3, 3)})
    assert move1 in [(0, 1), (1, 0), (0, 0)]
    pb2 = MyPoliceBrain((0, 0), 7)
    move2 = pb2._decide_move({"thief_pos": (3, 3)})
    assert move2 in [(0, 1), (1, 0), (0, 0)]
    pb3 = MyPoliceBrain((0, 0), 7)
    blocked_move = pb3._decide_move({"thief_pos": (3, 3)}, barriers=[(0, 1), (1, 0)])
    assert blocked_move == (0, 0)
