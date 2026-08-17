"""P2P server setup and tool registrations."""
import hashlib
from typing import Dict, Any
from src.network.mcp_server import FastMCPPeerServer

def create_p2p_server(name: str = "peer", port: int = 8802) -> FastMCPPeerServer:
    server = FastMCPPeerServer(name, port)
    
    # State for the commit-reveal protocol
    server.stored_commit = None

    def receive_commit(h_commit: str) -> Dict[str, str]:
        """Stores the opponent's SHA-256 hash and returns a locked acknowledgment."""
        server.stored_commit = h_commit
        return {"status": "locked_and_acknowledged"}

    def receive_reveal(state: str, move: str, intent: str, nonce: str) -> Dict[str, Any]:
        """Accepts the raw data, recalculates the SHA-256 hash, and compares it."""
        if not server.stored_commit:
            return {"status": "error", "message": "No commit received"}
            
        # Reconstruct canonical string and calculate hash
        data = f"{state}{move}{intent}{nonce}".encode('utf-8')
        calculated_hash = hashlib.sha256(data).hexdigest()
        
        if calculated_hash != server.stored_commit:
            return {"status": "TAMPERED", "technical_loss": True}
            
        # Reset for next round
        server.stored_commit = None
        return {"status": "verified"}

    server.register_tool("receive_commit", receive_commit)
    server.register_tool("receive_reveal", receive_reveal)
    
    return server
