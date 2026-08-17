"""Bayesian belief grid and posterior updating."""
from typing import Dict, List, Tuple
from src.shared.constants import GRID_SIZE

class BayesianBeliefGrid:
    def __init__(self, grid_size: int = GRID_SIZE):
        self.grid_size = grid_size
        total_cells = grid_size * grid_size
        self.probabilities: List[List[float]] = [
            [1.0 / total_cells for _ in range(grid_size)] for _ in range(grid_size)
        ]

    def update_with_scent(self, scent_matrix: List[List[float]]) -> None:
        total = 0.0
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                s = scent_matrix[r][c]
                likelihood = 1.0 + s * 2.0
                self.probabilities[r][c] *= likelihood
                total += self.probabilities[r][c]
        if total > 0:
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    self.probabilities[r][c] /= total

    def update_with_hint(self, reported_dir: str, weight: float = 0.6) -> None:
        reported_dir = reported_dir.lower()
        half_grid = self.grid_size / 2.0
        words = reported_dir.replace(",", " ").split()
        
        valid_dirs = {"north", "n", "south", "s", "east", "e", "west", "w"}
        if not any(d in words for d in valid_dirs):
            return
            
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                in_hemisphere = False
                if "north" in words or "n" in words:
                    if r < half_grid: in_hemisphere = True
                elif "south" in words or "s" in words:
                    if r >= half_grid: in_hemisphere = True
                elif "west" in words or "w" in words:
                    if c < half_grid: in_hemisphere = True
                elif "east" in words or "e" in words:
                    if c >= half_grid: in_hemisphere = True
                
                multiplier = weight if in_hemisphere else (1.0 - weight)
                self.probabilities[r][c] *= multiplier

    def normalize(self) -> None:
        total = sum(sum(row) for row in self.probabilities)
        if total > 0:
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    self.probabilities[r][c] /= total

    def get_most_likely_position(self) -> Tuple[int, int]:
        max_p = -1.0
        best = (0, 0)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self.probabilities[r][c] > max_p:
                    max_p = self.probabilities[r][c]
                    best = (r, c)
        return best

    def get_grid(self) -> List[List[float]]:
        return [row[:] for row in self.probabilities]
