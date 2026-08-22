"""Thief Evasion Brain strategy implementation using Minimax with Alpha-Beta Pruning."""
import random
from typing import Any, Dict, List, Optional, Tuple
from src.domain.distance import bfs_distance
from src.domain.grid import legal_moves
from src.strategy.base_brain import BrainBase

class ThiefBrain(BrainBase):
    def __init__(self, start_pos: Tuple[int, int] = (3, 3), grid_size: int = 7):
        super().__init__(grid_size=grid_size)
        self.position = start_pos
        self.cop_position_estimate = (0, 0)
        self.max_depth = 4

    def evaluate_state(self, thief_pos: Tuple[int, int], cop_pos: Tuple[int, int], barriers: Optional[List[Tuple[int, int]]]) -> float:
        if thief_pos == cop_pos:
            return -10000.0  # Captured
            
        dist = bfs_distance(thief_pos, cop_pos, grid_size=self.grid_size, barriers=barriers)
        
        # Wall-proximity penalty: discourage hugging edges and corners
        r, c = thief_pos
        max_edge = self.grid_size - 1
        wall_dist_r = min(r, max_edge - r)
        wall_dist_c = min(c, max_edge - c)
        min_wall_dist = min(wall_dist_r, wall_dist_c)

        wall_penalty = 0.0
        if min_wall_dist == 0:
            wall_penalty = -8.0
            if wall_dist_r == 0 and wall_dist_c == 0:
                wall_penalty = -20.0
        elif min_wall_dist == 1:
            wall_penalty = -3.0

        # Center-gravity bonus
        center = self.grid_size / 2.0
        center_bonus = -(abs(r - center) + abs(c - center)) * 0.5

        return (dist * 10.0) + wall_penalty + center_bonus

    def minimax(self, thief_pos: Tuple[int, int], cop_pos: Tuple[int, int], depth: int, alpha: float, beta: float, maximizingPlayer: bool, barriers: Optional[List[Tuple[int, int]]]) -> float:
        if depth == 0 or thief_pos == cop_pos:
            return self.evaluate_state(thief_pos, cop_pos, barriers)

        if maximizingPlayer:
            max_eval = -float('inf')
            valid_moves = [p.to_tuple() for p in legal_moves(thief_pos, grid_size=self.grid_size, barriers=barriers)]
            if not valid_moves:
                return self.evaluate_state(thief_pos, cop_pos, barriers)
                
            for child_pos in valid_moves:
                eval_score = self.minimax(child_pos, cop_pos, depth - 1, alpha, beta, False, barriers)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            valid_moves = [p.to_tuple() for p in legal_moves(cop_pos, grid_size=self.grid_size, barriers=barriers)]
            if not valid_moves:
                return self.evaluate_state(thief_pos, cop_pos, barriers)
                
            for child_pos in valid_moves:
                eval_score = self.minimax(thief_pos, child_pos, depth - 1, alpha, beta, True, barriers)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _pick_move(self, state: Dict[str, Any], belief_map: Any = None, valid_moves: Optional[List[Tuple[int, int]]] = None, barriers: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        if belief_map:
            cop_pos = belief_map.get_most_likely_position()
        else:
            cop_pos = state.get("cop_position", self.cop_position_estimate)

        self.cop_position_estimate = cop_pos

        if not valid_moves:
            valid_positions = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size, barriers=barriers)]
        else:
            valid_positions = valid_moves

        if not valid_positions:
            return self.position

        best_move = valid_positions[0]
        max_score = -float('inf')

        for move in valid_positions:
            score = self.minimax(move, cop_pos, self.max_depth, -float('inf'), float('inf'), False, barriers)
            if move == self.position:
                score -= 0.1  # slight penalty for standing still
            if score > max_score:
                max_score = score
                best_move = move
                
        self.position = best_move
        return best_move

    def _decide_move(self, state: Dict[str, Any], belief_map: Any = None, barriers: Optional[List[Tuple[int, int]]] = None) -> Tuple[int, int]:
        valid = [p.to_tuple() for p in legal_moves(self.position, grid_size=self.grid_size, barriers=barriers)]
        return self._pick_move(state, belief_map, valid_moves=valid, barriers=barriers)

    def _decide_bluff(self, state: Dict[str, Any], chosen_move: Tuple[int, int]) -> Tuple[str, bool]:
        if not hasattr(self, 'llm'):
            from src.infra.llm_provider import LLMProvider
            self.llm = LLMProvider(provider_type="template")

        hint_text = self.llm.generate_bluff(context=state, actual_move=str(chosen_move))
        return hint_text, False
