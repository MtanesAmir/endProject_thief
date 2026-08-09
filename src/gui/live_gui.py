"""Live GUI status banner and match tracker."""
from typing import Dict, Any

class LiveGUIController:
    def __init__(self):
        self.current_turn = "WAITING"
        self.status = "READY"

    def update_turn_banner(self, is_my_turn: bool) -> str:
        self.current_turn = "YOUR TURN" if is_my_turn else "LOCKED"
        return self.current_turn

    def render_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"banner": self.current_turn, "state": state}
