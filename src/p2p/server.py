"""FastMCP P2P Server module for Police agent."""

import hashlib
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
from typing import Any, Dict, Optional, List


class FastMCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler dispatching JSON-RPC requests to parent FastMCPServer."""

    server_instance: Optional["FastMCPServer"] = None

    def do_POST(self):
        """Handle incoming JSON-RPC POST requests."""
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len)

        try:
            req_data = json.loads(post_body.decode("utf-8"))
            if self.server_instance:
                res_data = self.server_instance.handle_jsonrpc(req_data)
            else:
                res_data = {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Server instance unavailable"}, "id": 1}
        except Exception as e:
            res_data = {"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {str(e)}"}, "id": 1}

        res_bytes = json.dumps(res_data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(res_bytes)))
        self.end_headers()
        self.wfile.write(res_bytes)

    def log_message(self, format, *args):
        """Silence standard request logging."""
import queue
import time
import asyncio
from typing import Dict, Any, Optional

class FastMCPServer:
    """Out-of-band P2P client to push FastMCP calls to opponent."""

    def __init__(self, opponent_url: Optional[str] = None):
        self.opponent_url = opponent_url
        self.queue = queue.Queue()
        self.is_running = False
        self._thread = None

    def start(self):
        if not self.opponent_url:
            return
        self.is_running = True
        import threading
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _worker_loop(self):
        asyncio.run(self._async_worker())

    async def _async_worker(self):
        from fastmcp import Client
        
        while self.is_running:
            try:
                # We hold the session open
                async with Client(self.opponent_url) as client:
                    while self.is_running:
                        try:
                            # Non-blocking get with short timeout to check is_running
                            method, payload = self.queue.get(timeout=0.5)
                            try:
                                arg_name = "payload" if method == "submit_audit" else "message"
                                await client.call_tool(method, {arg_name: payload})
                                print(f"Successfully pushed {method} to opponent")
                            except Exception as e:
                                print(f"Failed to push {method} to opponent: {e}")
                            finally:
                                self.queue.task_done()
                        except queue.Empty:
                            pass
                        except Exception as e:
                            print(f"Worker loop error: {e}")
                            await asyncio.sleep(1)
            except Exception as e:
                # Opponent not up yet or connection lost, retry
                print(f"Waiting for opponent at {self.opponent_url}: {e}")
                await asyncio.sleep(2)

    def call_opponent(self, method: str, params: Dict[str, Any]):
        """Enqueue an outbound tool call to the opponent."""
        if not self.opponent_url:
            return {"status": "error", "message": "No opponent URL configured"}
        self.queue.put((method, params))
        return {"status": "enqueued"}

