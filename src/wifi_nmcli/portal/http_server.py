"""http_server.py — Lifecycle manager for captive portal HTTP service."""
from __future__ import annotations

import http.server
import logging
import threading

from wifi_nmcli.core.constants import DEFAULT_PORTAL_PORT
from wifi_nmcli.portal.handlers import CaptivePortalHandler

logger = logging.getLogger(__name__)


class CaptiveHTTPServer:
    """Threaded HTTP server serving mobile Wi-Fi portal."""

    def __init__(self, port: int = DEFAULT_PORTAL_PORT) -> None:
        self.port = port
        self._server: http.server.ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> bool:
        if self._server: return True
        for candidate_port in (self.port, 8080):
            try:
                self._server = http.server.ThreadingHTTPServer(("0.0.0.0", candidate_port), CaptivePortalHandler)
                self.port = candidate_port
                self._thread = threading.Thread(target=self._server.serve_forever, name="CaptiveHTTP", daemon=True)
                self._thread.start()
                logger.info("Captive HTTP server running on port %d", self.port)
                return True
            except (OSError, PermissionError) as e:
                logger.warning("Port %d bind failed: %s", candidate_port, e)
        return False

    def stop(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except OSError: pass
            self._server = None
