import pytest
from src.domain.hardware import get_hardware_declaration

def test_hardware_declaration():
    decl = get_hardware_declaration("thief-team", "thief")
    assert decl["role"] == "thief"
    assert "os" in decl
    assert "cpu_count" in decl
