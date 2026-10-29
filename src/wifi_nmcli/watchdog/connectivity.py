"""connectivity.py — Network connectivity probe via socket connection."""
from __future__ import annotations

import socket

from wifi_nmcli.nmcli.runner import SIMULATION_STATE, is_nmcli_available


def is_network_connected(host: str = "1.1.1.1", port: int = 53, timeout: float = 2.0) -> bool:
    """Robust internet connectivity check via socket probes."""
    if not is_nmcli_available() and SIMULATION_STATE["enabled"]:
        return bool(SIMULATION_STATE.get("active_ssid"))

    for target in ((host, port), ("8.8.8.8", 53)):
        try:
            with socket.create_connection(target, timeout=timeout):
                return True
        except (TimeoutError, OSError):
            continue
    return False
