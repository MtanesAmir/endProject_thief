import pytest
from src.network.tunnel import TunnelManager


def test_tunnel_localhost_fallback():
    tm = TunnelManager()
    url = tm.start_tunnel(8802)
    assert url is not None
    assert "8802" in url
    assert url == "http://localhost:8802"
    tm.stop_tunnel()
    assert tm.public_url is None


def test_tunnel_ngrok_availability():
    tm = TunnelManager()
    assert isinstance(tm.is_ngrok_available(), bool)


def test_tunnel_with_authtoken():
    tm = TunnelManager(authtoken="fake-token-for-testing")
    assert tm.authtoken == "fake-token-for-testing"
    # Without real pyngrok, should fallback to localhost
    url = tm.start_tunnel(9999)
    assert "9999" in url
    tm.stop_tunnel()
    assert tm.public_url is None


def test_tunnel_stop_without_start():
    """Stopping a tunnel that was never started should not raise."""
    tm = TunnelManager()
    tm.stop_tunnel()
    assert tm.public_url is None
    assert tm._tunnel is None
