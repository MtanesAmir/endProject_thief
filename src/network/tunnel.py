"""Tunneling and NAT traversal helper."""
from typing import Optional

class TunnelManager:
    def __init__(self, authtoken: Optional[str] = None):
        self.authtoken = authtoken
        self.public_url: Optional[str] = None

    def start_tunnel(self, local_port: int) -> str:
        self.public_url = f"http://localhost:{local_port}"
        return self.public_url

    def stop_tunnel(self) -> None:
        self.public_url = None
