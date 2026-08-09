import pytest
from src.domain.belief import BayesianBeliefGrid

def test_bayesian_belief():
    grid = BayesianBeliefGrid(7)
    assert len(grid.get_grid()) == 7
    scent_matrix = [[0.0 for _ in range(7)] for _ in range(7)]
    scent_matrix[0][0] = 0.9
    grid.update_with_scent(scent_matrix)
    best_pos = grid.get_most_likely_position()
    assert best_pos == (0, 0)
