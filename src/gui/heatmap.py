"""GUI Heatmap visualizer."""
from typing import List

class HeatmapRenderer:
    def __init__(self, grid_size: int = 7):
        self.grid_size = grid_size

    def format_matrix_ascii(self, matrix: List[List[float]]) -> str:
        lines = []
        for row in matrix:
            line = " ".join(f"{val:4.2f}" for val in row)
            lines.append(line)
        return "\n".join(lines)
