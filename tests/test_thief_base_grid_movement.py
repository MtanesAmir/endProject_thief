import pytest
from src.domain.grid import GridPos, Direction, MovementEngine, legal_moves

def test_grid_pos_validity():
    p = GridPos(3, 3)
    assert p.is_valid(7) is True
    assert p.to_tuple() == (3, 3)
    invalid = GridPos(-1, 0)
    assert invalid.is_valid(7) is False

def test_legal_moves():
    moves = legal_moves((3, 3), grid_size=7)
    assert len(moves) == 5
    corner_moves = legal_moves((0, 0), grid_size=7)
    assert len(corner_moves) == 3

def test_movement_engine():
    engine = MovementEngine((3, 3), 7)
    assert engine.get_position() == GridPos(3, 3)
    assert engine.move(Direction.UP) is True
    assert engine.get_position() == GridPos(2, 3)
