"""FastMCP server wrapper."""
from typing import Any, Callable, Dict, Optional

class FastMCPPeerServer:
    def __init__(self, name: str = "thief_peer", port: int = 8802):
        self.name = name
        self.port = port
        self.handlers: Dict[str, Callable] = {}

    def register_tool(self, name: str, handler: Callable) -> None:
        self.handlers[name] = handler

    def handle_request(self, tool_name: str, **kwargs) -> Any:
        if tool_name in self.handlers:
            return self.handlers[tool_name](**kwargs)
        raise ValueError(f"Tool {tool_name} not registered")
