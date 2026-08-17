"""Tunneling and NAT traversal helper with pyngrok integration."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import pyngrok for real tunnel support
try:
    from pyngrok import ngrok as _ngrok

    _HAS_PYNGROK = True
except ImportError:
    _HAS_PYNGROK = False


class TunnelManager:
    """Manages ngrok tunnels for P2P connectivity across NATs.

    If ``pyngrok`` is installed and an authtoken is provided (or configured
    via ``ngrok config``), a real public tunnel is created.  Otherwise the
    manager falls back to a plain ``localhost`` URL so the rest of the code
    keeps working without external dependencies.
    """

    def __init__(self, authtoken: Optional[str] = None):
        self.authtoken = authtoken
        self.public_url: Optional[str] = None
        self._tunnel = None

    def start_tunnel(self, local_port: int) -> str:
        if _HAS_PYNGROK:
            try:
                if self.authtoken:
                    _ngrok.set_auth_token(self.authtoken)
                self._tunnel = _ngrok.connect(local_port, "http")
                self.public_url = self._tunnel.public_url
                logger.info("ngrok tunnel started: %s -> localhost:%d", self.public_url, local_port)
                return self.public_url
            except Exception as e:
                logger.warning("ngrok tunnel failed, falling back to localhost: %s", e)

        # Fallback: localhost URL
        self.public_url = f"http://localhost:{local_port}"
        logger.info("Using localhost fallback: %s", self.public_url)
        return self.public_url

    def stop_tunnel(self) -> None:
        if self._tunnel and _HAS_PYNGROK:
            try:
                _ngrok.disconnect(self._tunnel.public_url)
                logger.info("ngrok tunnel disconnected.")
            except Exception as e:
                logger.warning("Error disconnecting ngrok tunnel: %s", e)
        self._tunnel = None
        self.public_url = None

    def is_ngrok_available(self) -> bool:
        """Return True if pyngrok is installed and usable."""
        return _HAS_PYNGROK
