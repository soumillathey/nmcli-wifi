"""http_server.py — Lifecycle manager for captive portal HTTP service."""
from __future__ import annotations

import http.server
import logging
import threading

from wifi_nmcli.core.constants import DEFAULT_PORTAL_PORT
from wifi_nmcli.portal.handlers import CaptivePortalHandler
from wifi_nmcli.portal.redirect import kill_stale_portal_listeners, setup_port_forwarding, teardown_port_forwarding

logger = logging.getLogger(__name__)


class PortalThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class CaptiveHTTPServer:
    """Threaded HTTP server serving mobile Wi-Fi portal with port 80 self-healing."""

    def __init__(self, port: int = DEFAULT_PORTAL_PORT, iface: str = "wlan0") -> None:
        self.port, self.iface = port, iface
        self._server: PortalThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._redirected = False

    def start(self) -> bool:
        if self._server: return True
        kill_stale_portal_listeners(self.port)
        for _ in range(2):
            try:
                self._server = PortalThreadingHTTPServer(("0.0.0.0", self.port), CaptivePortalHandler)
                break
            except (OSError, PermissionError):
                kill_stale_portal_listeners(self.port)
        if not self._server:
            try:
                self._server = PortalThreadingHTTPServer(("0.0.0.0", 8080), CaptivePortalHandler)
                self.port = 8080
                self._redirected = setup_port_forwarding(self.iface, 80, 8080)
            except (OSError, PermissionError) as e:
                logger.error("Failed binding fallback port 8080: %s", e); return False

        self._thread = threading.Thread(target=self._server.serve_forever, name="CaptiveHTTP", daemon=True)
        self._thread.start()
        logger.info("Captive HTTP server running on port %d (iptables redirect=%s)", self.port, self._redirected)
        return True

    def stop(self) -> None:
        if self._redirected:
            teardown_port_forwarding(self.iface, 80, 8080); self._redirected = False
        if self._server:
            try: self._server.shutdown(); self._server.server_close()
            except OSError: pass
            self._server = None
