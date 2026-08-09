"""Replay log verification engine."""
import json
import hashlib
from typing import List, Dict, Any

class ReplayVerifier:
    @staticmethod
    def verify_entry(entry: Dict[str, Any]) -> bool:
        move = entry.get("move", "")
        nonce = entry.get("nonce", "")
        commit = entry.get("commit", "")
        payload = {"move": move, "nonce": nonce}
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(s.encode("utf-8")).hexdigest()
        return h == commit

    @staticmethod
    def verify_log(log: List[Dict[str, Any]]) -> str:
        for entry in log:
            if not ReplayVerifier.verify_entry(entry):
                return "TAMPERED"
        return "Verified OK"
