"""Thief Evasion Brain strategy implementation with Q-learning integration."""
import random
from typing import Any, Dict, List, Optional, Tuple
from src.domain.distance import manhattan_distance
from src.domain.grid import legal_moves
from src.strategy.base_brain import BrainBase
from src.strategy.q_learning import QLearningAgent

class ThiefBrain(BrainBase):
    def __init__(self, start_pos: Tuple[int, int] = (3, 3), grid_size: int = 7):
        super().__init__(grid_size=grid_size)
        self.position = start_pos
        self.cop_position_estimate = (0, 0)
        self.q_agent = QLearningAgent(alpha=0.1, gamma=0.95, epsilon=0.05)
        self._prev_state_key: Optional[str] = None
        self._prev_action: Optional[str] = None

    def _state_key(self, pos: Tuple[int, int], cop_est: Tuple[int, int]) -> str:
        """Serialize state for Q-table lookup."""
        return f"{pos[0]},{pos[1]}|{cop_est[0]},{cop_est[1]}"

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

        # Build state key for Q-learning
        current_state_key = self._state_key(self.position, cop_pos)
        action_keys = [str(m) for m in valid_positions]

        # Get Q-learning recommendation
        q_recommended = self.q_agent.choose_action(current_state_key, action_keys)

        best_move = valid_positions[0]
        max_score = -99999

        for move in valid_positions:
            dist = manhattan_distance(move, cop_pos)

            future_valid = [p.to_tuple() for p in legal_moves(move, grid_size=self.grid_size, barriers=barriers)]
            dof = len(future_valid)

            penalty = 0
            if dof <= 1:
                penalty = -100

            # Q-value bonus: reward moves that Q-learning has found effective
            q_bonus = self.q_agent.q_table.get((current_state_key, str(move)), 0.0) * 2.0

            score = dist + penalty + q_bonus
            if score > max_score:
                max_score = score
                best_move = move

        # Update Q-learning from previous step
        if self._prev_state_key is not None and self._prev_action is not None:
            prev_dist = manhattan_distance(self.position, cop_pos)
            new_dist = manhattan_distance(best_move, cop_pos)
            reward = new_dist - prev_dist  # Positive when we increased distance
            next_state_key = self._state_key(best_move, cop_pos)
            next_actions = [str(m) for m in valid_positions]
            self.q_agent.update(self._prev_state_key, self._prev_action, reward, next_state_key, next_actions)

        # Store current state/action for next update
        self._prev_state_key = current_state_key
        self._prev_action = str(best_move)

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
