import pytest
from src.network.tunnel import TunnelManager

def test_tunnel():
    tm = TunnelManager()
    url = tm.start_tunnel(8802)
    assert "8802" in url
    tm.stop_tunnel()
    assert tm.public_url is None
