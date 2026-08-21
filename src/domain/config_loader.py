"""Configuration loader supporting JSON shared contract and TOML private config."""
import json
import os
from typing import Any, Dict

def load_shared_contract(path: str = "config/game.json") -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def load_peer_config(path: str = "config/game.toml") -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        import tomli
        with open(path, "rb") as f:
            return tomli.load(f)
    except Exception:
        return {}
