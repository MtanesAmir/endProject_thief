"""Tests for FastMCP HTTP handler and async worker."""
import pytest
import json
import asyncio
import threading
from unittest.mock import patch, MagicMock, AsyncMock
from src.p2p.server import FastMCPHTTPHandler, FastMCPServer

def test_fastmcp_http_handler_do_post():
    """Test the HTTP handler JSON-RPC dispatch."""
    mock_request = MagicMock()
    mock_client_address = ("127.0.0.1", 12345)
    mock_server = MagicMock()
    
    # We don't want to actually start a socket, just test do_POST.
    # Instantiate handler without calling __init__ which tries to use the socket.
    handler = FastMCPHTTPHandler.__new__(FastMCPHTTPHandler)
    handler.rfile = MagicMock()
    handler.wfile = MagicMock()
    handler.headers = {"Content-Length": "15"}
    
    # Valid JSON
    handler.rfile.read.return_value = b'{"method":"hi"}'
    
    handler.server_instance = MagicMock()
    handler.server_instance.handle_jsonrpc.return_value = {"result": "ok"}
    
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    
    handler.do_POST()
    handler.server_instance.handle_jsonrpc.assert_called_once_with({"method": "hi"})
    handler.wfile.write.assert_called_once()
    response_bytes = handler.wfile.write.call_args[0][0]
    assert b'"result": "ok"' in response_bytes

def test_fastmcp_http_handler_no_server():
    """Test HTTP handler when no server instance is attached."""
    handler = FastMCPHTTPHandler.__new__(FastMCPHTTPHandler)
    handler.rfile = MagicMock()
    handler.wfile = MagicMock()
    handler.headers = {"Content-Length": "2"}
    handler.rfile.read.return_value = b'{}'
    handler.server_instance = None
    
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    
    handler.do_POST()
    response_bytes = handler.wfile.write.call_args[0][0]
    assert b'Server instance unavailable' in response_bytes

def test_fastmcp_server_start_stop():
    """Test thread lifecycle for FastMCPServer."""
    server = FastMCPServer("http://test")
    
    # Mock the internal worker to block until stop is called
    import time
    def mock_worker():
        while server.is_running:
            time.sleep(0.01)
            
    server._worker_loop = mock_worker
    
    server.start()
    assert server.is_running
    assert server._thread is not None
    assert server._thread.is_alive()
    
    server.stop()
    assert not server.is_running
    assert not server._thread.is_alive()

def test_fastmcp_server_async_worker():
    """Test the async worker pulls from queue and calls client."""
    server = FastMCPServer("http://test")
    server.is_running = True
    server.queue.put(("test_method", {"data": 1}))
    
    mock_client_instance = AsyncMock()
    
    class MockClientContext:
        async def __aenter__(self):
            return mock_client_instance
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    # We want to run the loop exactly once then stop it
    original_get = server.queue.get
    def mock_get(timeout):
        server.is_running = False # stop loop after one get
        return original_get(timeout=timeout)
        
    server.queue.get = mock_get
    
    with patch("fastmcp.Client", return_value=MockClientContext()):
        asyncio.run(server._async_worker())
        
    mock_client_instance.call_tool.assert_called_once_with("test_method", {"message": {"data": 1}})
