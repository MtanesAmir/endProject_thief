"""Stigmergic scent emission and decay model."""
import math
from typing import List, Tuple
from src.shared.constants import DEFAULT_RHO, DEFAULT_TAU_CENTER, GRID_SIZE

class ScentTracker:
    def __init__(self, grid_size: int = GRID_SIZE):
        self.grid_size = grid_size
        self.matrix: List[List[float]] = [[0.0 for _ in range(grid_size)] for _ in range(grid_size)]

    def apply_emission(self, center_pos: Tuple[int, int], tau_center: float = DEFAULT_TAU_CENTER) -> None:
        r_c, c_c = center_pos
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = r_c + dr, c_c + dc
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                    dist = math.sqrt(dr * dr + dc * dc)
                    intensity = tau_center / (1.0 + dist)
                    self.matrix[r][c] += intensity

    def apply_decay(self, rho: float = DEFAULT_RHO) -> None:
        retention = 1.0 - rho
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                self.matrix[r][c] = max(0.0, retention * self.matrix[r][c])

    def get_scent_level(self, pos: Tuple[int, int]) -> float:
        r, c = pos
        return self.matrix[r][c] if (0 <= r < self.grid_size and 0 <= c < self.grid_size) else 0.0

    def get_matrix(self) -> List[List[float]]:
        return [row[:] for row in self.matrix]

    def reset(self) -> None:
        self.matrix = [[0.0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
