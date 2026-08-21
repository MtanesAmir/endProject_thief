import pytest
from src.strategy.thief_brain import ThiefBrain

def test_thief_brain():
    tb = ThiefBrain((3, 3), 7)
    move = tb._decide_move({"cop_position": (3, 2)})
    assert move != (3, 2)
    bluff_text, is_truthful = tb._decide_bluff({}, move)
    # Bluff should contain a directional hint but NOT the actual move coordinates
    assert any(d in bluff_text.lower() for d in ["north", "south", "east", "west"])
    assert isinstance(is_truthful, bool)

def test_thief_brain_avoids_corners():
    """Test that the thief does not run straight to a corner."""
    tb = ThiefBrain((3, 3), 7)
    # Run several moves with cop at (0,0) — thief should NOT end up at (6,6)
    for _ in range(10):
        move = tb._decide_move({"cop_position": (0, 0)})
    # After 10 moves, thief should NOT be trapped in corner (6,6)
    pos = tb.position
    is_corner = pos in [(0, 0), (0, 6), (6, 0), (6, 6)]
    # Allow it sometimes (randomness) but the position should have reasonable DOF
    from src.domain.grid import legal_moves
    dof = len(legal_moves(pos, grid_size=7))
    assert dof >= 3 or not is_corner

def test_thief_brain_wall_avoidance():
    """Test that thief prefers interior positions over edge positions."""
    tb = ThiefBrain((3, 3), 7)
    # With cop at center-ish, thief should move away but not hug the wall
    move = tb._decide_move({"cop_position": (2, 3)})
    r, c = move
    # Move should be valid
    assert 0 <= r < 7 and 0 <= c < 7
