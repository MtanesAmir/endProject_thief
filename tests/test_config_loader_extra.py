"""Test config loader exception handling."""
import pytest
from src.domain.config_loader import load_shared_contract

def test_config_loader_invalid_json(tmp_path):
    """Test loading invalid JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("INVALID JSON")
    result = load_shared_contract(str(bad_file))
    assert result == {}
