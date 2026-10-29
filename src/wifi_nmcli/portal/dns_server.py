"""dns_server.py — Intercepts all DNS queries and resolves them to portal IP."""
from __future__ import annotations

import logging
import socket
import threading

from wifi_nmcli.core.constants import DEFAULT_DNS_PORT, DEFAULT_GATEWAY_IP

logger = logging.getLogger(__name__)


def _build_response(data: bytes, ip: str) -> bytes:
    tid, flags = data[:2], 0x8180
    qcount, ancount = 1, 1
    header = tid + flags.to_bytes(2, "big") + qcount.to_bytes(2, "big") + ancount.to_bytes(2, "big") + b"\x00\x00\x00\x00"
    question_end = data.find(b"\x00", 12) + 5
    question = data[12:question_end]
    answer = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton(ip)
    return header + question + answer


class CaptiveDNSServer:
    """Lightweight UDP DNS resolver redirecting all queries to captive portal."""

    def __init__(self, ip: str = DEFAULT_GATEWAY_IP, port: int = DEFAULT_DNS_PORT) -> None:
        self.ip, self.port = ip, port
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> bool:
        if self._running: return True
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.bind(("0.0.0.0", self.port))
            self._running = True
            self._thread = threading.Thread(target=self._serve, name="CaptiveDNS", daemon=True)
            self._thread.start()
            logger.info("Captive DNS server listening on UDP %s:%d", self.ip, self.port)
            return True
        except (OSError, PermissionError) as e:
            logger.warning("DNS server bind failed (port %d): %s", self.port, e)
            return False

    def _serve(self) -> None:
        while self._running and self._sock:
            try:
                data, addr = self._sock.recvfrom(512)
                if len(data) >= 12: self._sock.sendto(_build_response(data, self.ip), addr)
            except OSError: break

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try: self._sock.close()
            except OSError: pass
            self._sock = None
