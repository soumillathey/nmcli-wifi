"""ip.py — Network interface IP detection for captive hotspot."""
from __future__ import annotations

import socket

from wifi_nmcli.core.constants import DEFAULT_GATEWAY_IP


def get_hotspot_ip(iface: str | None = None) -> str:
    """Get the current IP address assigned to the hotspot interface."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return DEFAULT_GATEWAY_IP
