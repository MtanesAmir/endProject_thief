"""Tests for strategy missing branches."""
import pytest
from src.strategy.police_brain import MyPoliceBrain
from src.strategy.thief_brain import ThiefBrain

def test_police_brain_no_moves():
    """Test police brain when trapped."""
    pb = MyPoliceBrain((0, 0), 7)
    # mock legal moves
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.strategy.police_brain.legal_moves", lambda *a, **k: [])
        move = pb._decide_move({"thief_position": (3,3)})
        assert move == (0, 0)

def test_police_brain_no_min_dist():
    """Test police brain when no moves are better than 999."""
    pb = MyPoliceBrain((0, 0), 7)
    class FakePos:
        def to_tuple(self): return (1,1)
    
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.strategy.police_brain.legal_moves", lambda *a, **k: [FakePos()])
        m.setattr("src.strategy.police_brain.manhattan_distance", lambda *a, **k: 1000)
        move = pb._decide_move({"thief_position": (3,3)})
        assert move == (1, 1)

def test_thief_brain_no_valid_moves_passed():
    """Test thief brain when valid_moves is empty/none."""
    tb = ThiefBrain((3, 3), 7)
    move = tb._decide_move({"cop_position": (0,0)})
    assert move != (3, 3)
    
def test_thief_brain_trapped():
    """Test thief brain when completely trapped."""
    tb = ThiefBrain((3, 3), 7)
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.strategy.thief_brain.legal_moves", lambda *a, **k: [])
        move = tb._decide_move({"cop_position": (0,0)})
        assert move == (3, 3)
        
def test_thief_brain_dead_end_penalties():
    """Test thief brain evaluates dead-end branches."""
    tb = ThiefBrain((3, 3), 7)
    
    class FakePos:
        def __init__(self, pos): self.pos = pos
        def to_tuple(self): return self.pos
        
    def mock_legal_moves(pos, *a, **k):
        # When evaluating moves from (3,3), return (3,4) and (3,2)
        if pos == (3,3):
            return [FakePos((3,4)), FakePos((3,2))]
        # When evaluating (3,4)'s future, return 1 move (dof=1)
        if pos == (3,4):
            return [FakePos((3,5))]
        # When evaluating (3,2)'s future, return 2 moves (dof=2)
        if pos == (3,2):
            return [FakePos((3,1)), FakePos((2,2))]
        return []

    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.strategy.thief_brain.legal_moves", mock_legal_moves)
        move = tb._decide_move({"cop_position": (0,0)})
        # It should pick (3,2) because dof=2 penalty (-30) is better than dof=1 penalty (-100)
        assert move == (3, 2)
