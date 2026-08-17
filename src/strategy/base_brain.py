"""Abstract base brain class for multi-agent strategy engines."""
from typing import Any, Dict, List, Optional, Tuple

GRID_SIZE = 7
ACTIONS = {
    "STAY": (0, 0),
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

class BrainBase:
    def __init__(self, grid_size: int = GRID_SIZE):
        self.grid_size = grid_size

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size

    def _pick_move(self, state: Dict[str, Any], belief_map: Any = None) -> Tuple[int, int]:
        raise NotImplementedError

    def _decide_move(self, state: Dict[str, Any], belief_map: Any = None, barriers: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        raise NotImplementedError
