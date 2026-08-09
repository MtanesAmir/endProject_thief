"""Thief Evasion Brain strategy implementation."""
import random
from typing import Any, Dict, List, Optional, Tuple
from src.domain.distance import manhattan_distance
from src.domain.grid import legal_moves
from src.strategy.base_brain import BrainBase

class ThiefBrain(BrainBase):
    def __init__(self, start_pos: Tuple[int, int] = (3, 3), grid_size: int = 7):
        super().__init__(grid_size=grid_size)
        self.position = start_pos
        self.cop_position_estimate = (0, 0)

    def _pick_move(self, state: Dict[str, Any], valid_moves: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        cop_pos = state.get("cop_position", self.cop_position_estimate)
        self.cop_position_estimate = cop_pos

        if not valid_moves:
            valid_positions = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size)]
        else:
            valid_positions = valid_moves

        if not valid_positions:
            return self.position

        best_move = valid_positions[0]
        max_dist = -1
        for move in valid_positions:
            dist = manhattan_distance(move, cop_pos)
            if dist > max_dist:
                max_dist = dist
                best_move = move

        self.position = best_move
        return best_move

    def _decide_move(self, state: Dict[str, Any], barriers: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        valid = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size, barriers=barriers)]
        return self._pick_move(state, valid_moves=valid)

    def _decide_bluff(self, state: Dict[str, Any], chosen_move: Tuple[int, int]) -> str:
        dirs = ["N", "S", "E", "W"]
        return f"I moved {random.choice(dirs)}"
