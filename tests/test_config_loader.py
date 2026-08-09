import pytest
from src.domain.config_loader import load_shared_contract, load_peer_config

def test_config_loaders():
    shared = load_shared_contract("config/game.json")
    assert shared.get("schema_version") == "1.2"
    peer = load_peer_config("config/game.toml")
    assert isinstance(peer, dict)
