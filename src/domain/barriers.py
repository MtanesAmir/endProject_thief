"""Barrier management and spatial obstacle verification."""
from typing import List, Optional, Set, Tuple, Union
from src.domain.grid import GridPos
from src.shared.constants import MAX_BARRIERS

class BarrierManager:
    def __init__(self, max_barriers: int = MAX_BARRIERS, grid_size: int = 7):
        self.max_barriers = max_barriers
        self.grid_size = grid_size
        self.barriers: Set[Tuple[int, int]] = set()

    def add_barrier(self, pos: Union[GridPos, Tuple[int, int]]) -> bool:
        p = pos.to_tuple() if isinstance(pos, GridPos) else pos
        if len(self.barriers) >= self.max_barriers:
            return False
        if not (0 <= p[0] < self.grid_size and 0 <= p[1] < self.grid_size):
            return False
        self.barriers.add(p)
        return True

    def is_blocked(self, pos: Union[GridPos, Tuple[int, int]]) -> bool:
        p = pos.to_tuple() if isinstance(pos, GridPos) else pos
        return p in self.barriers

    def get_barriers(self) -> List[Tuple[int, int]]:
        return sorted(list(self.barriers))

    def count(self) -> int:
        return len(self.barriers)

    def clear(self) -> None:
        self.barriers.clear()
