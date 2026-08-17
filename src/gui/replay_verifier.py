"""Replay log verification engine."""
import json
import hashlib
import secrets
from typing import List, Dict, Any

class ReplayVerifier:
    @staticmethod
    def verify_entry(entry: Dict[str, Any]) -> bool:
        move = entry.get("move", "")
        nonce = entry.get("nonce", "")
        commit = entry.get("commit", "")
        state = entry.get("state", {})
        intent = entry.get("hint", "")
        
        payload = {"intent": intent, "move": move, "nonce": nonce, "state": state}
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(s.encode("utf-8")).hexdigest()
        
        return secrets.compare_digest(commit, h)

    @staticmethod
    def verify_log(log: List[Dict[str, Any]]) -> Dict[str, Any]:
        for entry in log:
            if not ReplayVerifier.verify_entry(entry):
                return {"status": "TAMPERED", "cop_score": 0, "thief_score": 0}
        return {"status": "VERIFIED_OK"}
