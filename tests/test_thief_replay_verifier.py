import pytest
from src.gui.replay_verifier import ReplayVerifier
import json, hashlib

def test_replay_verifier():
    payload = {"move": "(3, 3)", "nonce": "123456"}
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    log = [{"move": "(3, 3)", "nonce": "123456", "commit": h}]
    assert ReplayVerifier.verify_log(log) == "Verified OK"
    tampered = [{"move": "(3, 4)", "nonce": "123456", "commit": h}]
    assert ReplayVerifier.verify_log(tampered) == "TAMPERED"
