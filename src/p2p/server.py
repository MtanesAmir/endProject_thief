"""P2P server setup and tool registrations."""
from typing import Any, Dict
from src.network.mcp_server import FastMCPPeerServer

def create_thief_p2p_server(port: int = 8802, on_move_callback: Any = None) -> FastMCPPeerServer:
    server = FastMCPPeerServer("thief_peer", port)

    def receive_move(signed_move: str, signature: str) -> Dict[str, Any]:
        if on_move_callback:
            return on_move_callback(signed_move, signature)
        return {"status": "accepted", "signed_move": signed_move}

    server.register_tool("receive_move", receive_move)
    return server
