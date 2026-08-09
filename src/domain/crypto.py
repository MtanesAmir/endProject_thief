"""SHA-256 Commit-Reveal cryptographic protocol engine."""
import hashlib
import json
import secrets
from typing import Any, Optional, Tuple

class CommitmentScheme:
    @staticmethod
    def generate_nonce(num_bytes: int = 16) -> str:
        return secrets.token_hex(num_bytes)

    @staticmethod
    def canonical_serialize(payload: Any) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def create_commitment(self, move: Any, nonce: Optional[str] = None) -> Tuple[str, str]:
        if nonce is None:
            nonce = self.generate_nonce(16)
        payload = {"move": move, "nonce": nonce}
        h = hashlib.sha256(self.canonical_serialize(payload).encode("utf-8")).hexdigest()
        return h, nonce

    def verify_reveal(self, commitment: str, move: Any, nonce: str) -> bool:
        h, _ = self.create_commitment(move, nonce)
        return secrets.compare_digest(commitment, h)


class CommitRevealEngine:
    def __init__(self):
        self.scheme = CommitmentScheme()

    def commit(self, state: Any, move: Any, intent: Any = None, nonce: Optional[str] = None) -> Tuple[str, str]:
        if nonce is None:
            nonce = self.scheme.generate_nonce(16)
        payload = {"intent": intent, "move": move, "nonce": nonce, "state": state}
        h = hashlib.sha256(self.scheme.canonical_serialize(payload).encode("utf-8")).hexdigest()
        return h, nonce

    def verify(self, commitment: str, state: Any, move: Any, intent: Any, nonce: str) -> bool:
        payload = {"intent": intent, "move": move, "nonce": nonce, "state": state}
        h = hashlib.sha256(self.scheme.canonical_serialize(payload).encode("utf-8")).hexdigest()
        return secrets.compare_digest(commitment, h)
