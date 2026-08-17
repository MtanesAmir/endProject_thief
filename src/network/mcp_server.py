"""FastMCP server wrapper."""
from typing import Any, Callable
from fastmcp import FastMCP

class FastMCPPeerServer:
    def __init__(self, name: str = "thief_peer", port: int = 8802):
        self.name = name
        self.port = port
        self.mcp = FastMCP(name)

    def register_tool(self, name: str, handler: Callable) -> None:
        handler.__name__ = name
        self.mcp.add_tool(handler)

    def run(self) -> None:
        self.mcp.run(transport="sse", port=self.port, host="127.0.0.1")
