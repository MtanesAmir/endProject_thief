"""Local police pursuit simulator brain."""
from typing import Any, Dict, List, Optional, Tuple
from src.domain.distance import bfs_distance
from src.domain.grid import legal_moves
from src.strategy.base_brain import BrainBase

class MyPoliceBrain(BrainBase):
    def __init__(self, start_pos: Tuple[int, int] = (0, 0), grid_size: int = 7):
        super().__init__(grid_size=grid_size)
        self.position = start_pos

    def _pick_move(self, state: Dict[str, Any]) -> Tuple[int, int]:
        thief_pos = state.get("thief_pos", (3, 3))
        valid = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size)]
        if not valid:
            return self.position
            
        best = valid[0]
        min_d = 9999
        for m in valid:
            d = bfs_distance(m, thief_pos, grid_size=self.grid_size)
            if d < min_d:
                min_d = d
                best = m
        self.position = best
        return best

    def _decide_move(self, state: Dict[str, Any], barriers: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        valid = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size, barriers=barriers)]
        if not valid:
            return self.position
            
        thief_pos = state.get("thief_pos", (3, 3))
        best = valid[0]
        min_d = 9999
        
        for m in valid:
            d = bfs_distance(m, thief_pos, grid_size=self.grid_size, barriers=barriers)
            # Tie breaker: if distance is the same, pick the one closer to center to cut off routes? Or just pick first
            if d < min_d:
                min_d = d
                best = m
                
        self.position = best
        return best
