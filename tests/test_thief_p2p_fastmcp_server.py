import pytest
from src.p2p.server import create_thief_p2p_server

def test_p2p_server():
    server = create_thief_p2p_server(8802)
    res = server.handle_request("receive_move", signed_move="move_sig", signature="sig")
    assert res["status"] == "accepted"
