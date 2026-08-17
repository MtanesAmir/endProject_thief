"""P2P server setup and tool registrations."""
import json
from typing import Dict, Any
from src.network.mcp_server import FastMCPPeerServer
from src.domain.crypto import CommitRevealEngine

def create_p2p_server(name: str = "peer", port: int = 8802) -> FastMCPPeerServer:
    server = FastMCPPeerServer(name, port)

    # State for the commit-reveal protocol
    server.stored_commit = None
    server.crypto_engine = CommitRevealEngine()

    def receive_commit(h_commit: str) -> Dict[str, str]:
        """Stores the opponent's SHA-256 hash and returns a locked acknowledgment."""
        server.stored_commit = h_commit
        return {"status": "locked_and_acknowledged"}

    def receive_reveal(state: str, move: str, intent: str, nonce: str) -> Dict[str, Any]:
        """Accepts the raw data, verifies commitment using canonical JSON, and compares."""
        if not server.stored_commit:
            return {"status": "error", "message": "No commit received"}

        # Parse intent back to its original form if it was JSON-serialized
        try:
            intent_obj = json.loads(intent)
        except (json.JSONDecodeError, TypeError):
            intent_obj = intent

        # Use the same canonical JSON verification as the crypto engine
        verified = server.crypto_engine.verify(
            commitment=server.stored_commit,
            state=state,
            move=move,
            intent=intent_obj,
            nonce=nonce,
        )

        if not verified:
            return {"status": "TAMPERED", "technical_loss": True}

        # Reset for next round
        server.stored_commit = None
        return {"status": "verified"}

    server.register_tool("receive_commit", receive_commit)
    server.register_tool("receive_reveal", receive_reveal)

    return server
