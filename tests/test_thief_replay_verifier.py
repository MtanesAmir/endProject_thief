import pytest
from src.gui.replay_verifier import ReplayVerifier
import json, hashlib

def test_replay_verifier():
    # Build a valid entry matching ReplayVerifier.verify_entry's expected payload structure
    move = "(3, 3)"
    nonce = "123456"
    state = {}
    hint = ""
    payload = {"intent": hint, "move": move, "state": state}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    seed = f"{s}|{nonce}"
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    log = [{"move": move, "nonce": nonce, "commit": h, "state": state, "hint": hint}]
    result = ReplayVerifier.verify_log(log)
    assert result["status"] == "VERIFIED_OK"

def test_replay_tampered():
    move = "(3, 3)"
    nonce = "123456"
    state = {}
    hint = ""
    payload = {"intent": hint, "move": move, "state": state}
    s = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    seed = f"{s}|{nonce}"
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    tampered = [{"move": "(3, 4)", "nonce": nonce, "commit": h, "state": state, "hint": hint}]
    result = ReplayVerifier.verify_log(tampered)
    assert result["status"] == "TAMPERED"
