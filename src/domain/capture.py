"""Capture mechanics and end-of-game outcome determination."""
from typing import Dict, Tuple, Union
from src.domain.grid import GridPos
from src.shared.constants import (
    MAX_MOVES, SCORE_CAPTURE_COP, SCORE_CAPTURE_THIEF,
    SCORE_SURVIVAL_COP, SCORE_SURVIVAL_THIEF, SCORE_TECHNICAL_LOSS
)

def is_captured(cop_pos: Union[GridPos, Tuple[int, int]], thief_pos: Union[GridPos, Tuple[int, int]]) -> bool:
    c = cop_pos.to_tuple() if isinstance(cop_pos, GridPos) else cop_pos
    t = thief_pos.to_tuple() if isinstance(thief_pos, GridPos) else thief_pos
    return c == t

def evaluate_match_result(
    cop_pos: Tuple[int, int],
    thief_pos: Tuple[int, int],
    current_step: int,
    max_steps: int = MAX_MOVES,
    disqualified_role: str = ""
) -> Dict[str, Union[str, int, bool]]:
    if disqualified_role == "police":
        return {"outcome": "THIEF_WIN_DISQUALIFICATION", "cop_score": 0, "thief_score": SCORE_SURVIVAL_THIEF, "terminal": True}
    if disqualified_role == "thief":
        return {"outcome": "COP_WIN_DISQUALIFICATION", "cop_score": SCORE_CAPTURE_COP, "thief_score": 0, "terminal": True}

    if is_captured(cop_pos, thief_pos):
        return {"outcome": "COP_CAPTURE", "cop_score": SCORE_CAPTURE_COP, "thief_score": SCORE_CAPTURE_THIEF, "terminal": True}

    if current_step >= max_steps:
        return {"outcome": "THIEF_SURVIVAL", "cop_score": SCORE_SURVIVAL_COP, "thief_score": SCORE_SURVIVAL_THIEF, "terminal": True}

    return {"outcome": "ONGOING", "cop_score": 0, "thief_score": 0, "terminal": False}
