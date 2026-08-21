"""Tests for tunnel exception handling."""
import pytest
from unittest.mock import patch, MagicMock
from src.network.tunnel import TunnelManager

def test_tunnel_not_available():
    """Test tunnel start when ngrok is unavailable."""
    import src.network.tunnel as tunnel_module
    tunnel_module._HAS_PYNGROK = False
    manager = tunnel_module.TunnelManager()
    url = manager.start_tunnel(8000)
    assert url == "http://localhost:8000"

def test_tunnel_stop_exception():
    """Test tunnel stop logs exception and continues."""
    import src.network.tunnel as tunnel_module
    tunnel_module._HAS_PYNGROK = True
    manager = tunnel_module.TunnelManager()
    manager._tunnel = MagicMock()
    with patch("pyngrok.ngrok.disconnect", side_effect=Exception("disconnect error")):
        manager.stop_tunnel()
