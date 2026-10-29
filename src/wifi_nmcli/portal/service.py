"""service.py — Unified manager for DNS and HTTP captive portal services."""
from __future__ import annotations

import logging

from wifi_nmcli.core.constants import (
    DEFAULT_DNS_PORT,
    DEFAULT_GATEWAY_IP,
    DEFAULT_PORTAL_PORT,
)
from wifi_nmcli.portal.dns_server import CaptiveDNSServer
from wifi_nmcli.portal.http_server import CaptiveHTTPServer

logger = logging.getLogger(__name__)


class PortalService:
    def __init__(self) -> None:
        self._dns: CaptiveDNSServer | None = None
        self._http: CaptiveHTTPServer | None = None
        self._active = False

    def is_running(self) -> bool:
        return self._active

    def start(self, ip: str = DEFAULT_GATEWAY_IP, http_port: int = DEFAULT_PORTAL_PORT, dns_port: int = DEFAULT_DNS_PORT) -> bool:
        if self._active: return True
        self._dns = CaptiveDNSServer(ip=ip, port=dns_port)
        self._http = CaptiveHTTPServer(port=http_port)
        dns_ok, http_ok = self._dns.start(), self._http.start()
        self._active = http_ok
        logger.info("Captive portal status: HTTP=%s, DNS=%s", http_ok, dns_ok)
        return self._active

    def stop(self) -> None:
        if self._dns: self._dns.stop(); self._dns = None
        if self._http: self._http.stop(); self._http = None
        self._active = False
        logger.info("Captive portal stopped.")


portal_service = PortalService()
