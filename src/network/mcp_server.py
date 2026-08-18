"""Network MCP server wrapper module implementing the standard Dec-POMDP tools."""

import os
import sys
from typing import Dict, Any

# Add the kit to sys.path to construct valid Greetings
kit_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../copthief-league-protocol"))
if kit_path not in sys.path:
    sys.path.append(kit_path)

from fastmcp import FastMCP
from src.core.orchestrator import ThiefOrchestrator
from src.p2p.server import FastMCPServer

# Initialize FastMCP Server
mcp = FastMCP("thief_peer")

# Global instances
opponent_url = os.environ.get("OPPONENT_URL")
p2p_client = FastMCPServer(opponent_url=opponent_url) if opponent_url else None
if p2p_client:
    p2p_client.start()
orchestrator = ThiefOrchestrator(p2p_server=p2p_client)

@mcp.tool
def negotiate(message: Dict[str, Any]) -> Dict[str, Any]:
    """Receive the opponent's signed game agreement."""
    # We accept the turn_init
    result = orchestrator.handle_incoming_message("negotiate", message)
    
    # Generate our own agreement and push it back to the opponent
    try:
        from sparring.negotiate import our_greeting
        from sparring.config import SparConfig
        from sparring.identity import locks
        
        cfg = SparConfig(group_id="thief_group", group_name="Thief Team", seed=123)
        n = message.get("sub_game_number", 1)
        opponent_group = message.get("group_id", "opponent")
        lock_hashes = locks(cfg.scent_model)
        
        mine = our_greeting(cfg, "thief", n, f"{n:032x}", lock_hashes, opponent_group)
        if p2p_client:
            p2p_client.call_opponent("negotiate", mine.to_wire())
            print("Pushed our agreement back to opponent!")
            # Since we are Thief, we move first! Trigger the first turn!
            import threading
            import time
            def delayed_start():
                time.sleep(1.0)
                orchestrator.handle_incoming_message("PROCESS_TURN", {})
            threading.Thread(target=delayed_start, daemon=True).start()
    except Exception as e:
        print(f"Failed to generate and push agreement: {e}")
        
    return result

@mcp.tool
def receive_turn(message: Dict[str, Any]) -> Dict[str, Any]:
    """Receive the opponent's turn message."""
    return orchestrator.handle_incoming_message("receive_turn", message)

@mcp.tool
def submit_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Receive the opponent's end-of-game audit reveal (records + nonces)."""
    result = orchestrator.handle_incoming_message("submit_audit", payload)
    if p2p_client:
        my_audit = {
            "sender": "thief",
            "records": [],
            "result_claim": "survival"
        }
        try:
            p2p_client.call_opponent("submit_audit", my_audit)
            print("Pushed our audit back to opponent!")
        except Exception as e:
            print(f"Failed to push audit: {e}")
    return result

@mcp.tool
def receive_control(message: Dict[str, Any]) -> Dict[str, Any]:
    """Receive an opponent control signal (enable / status / restart / quit)."""
    return orchestrator.handle_incoming_message("receive_control", message)

__all__ = ["mcp", "orchestrator"]

if __name__ == "__main__":
    # Ensure transport and port are specified so FastMCP runs continuously
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
