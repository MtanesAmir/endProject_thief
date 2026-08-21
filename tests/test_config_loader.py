import pytest
from src.domain.config_loader import load_shared_contract, load_peer_config

def test_config_loaders():
    shared = load_shared_contract("config/game.json")
    assert shared.get("schema_version") == "1.2"
    peer = load_peer_config("config/game.toml")
    assert isinstance(peer, dict)

def test_config_loader_missing_shared():
    """Test loading a non-existent shared contract returns empty dict."""
    result = load_shared_contract("nonexistent/file.json")
    assert result == {}

def test_config_loader_missing_peer():
    """Test loading a non-existent peer config returns empty dict."""
    result = load_peer_config("nonexistent/file.toml")
    assert result == {}

def test_config_loader_shared_content():
    """Test shared contract has expected fields."""
    shared = load_shared_contract("config/game.json")
    assert "board_and_agents" in shared
    assert shared["board_and_agents"]["grid_size"] == 7
    assert "scoring" in shared
    assert "pheromones" in shared
