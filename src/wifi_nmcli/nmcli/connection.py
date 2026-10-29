"""connection.py — Handles Wi-Fi client connections via nmcli."""
from __future__ import annotations

import logging

from wifi_nmcli.core.constants import DEFAULT_CONNECT_TIMEOUT
from wifi_nmcli.nmcli.runner import (
    SIMULATION_STATE,
    get_wifi_interface,
    is_nmcli_available,
    run_nmcli,
)

logger = logging.getLogger(__name__)


def get_active_wifi_ssid() -> str | None:
    """Return the currently connected Wi-Fi SSID if any."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        return str(SIMULATION_STATE.get("active_ssid", "")) or None
    code, out = run_nmcli(["-t", "-f", "TYPE,NAME,DEVICE", "connection", "show", "--active"])
    if code != 0:
        return None
    for line in out.splitlines():
        parts = line.strip().split(":")
        if len(parts) >= 2 and ("802-11-wireless" in parts[0] or "wifi" in parts[0]):
            return parts[1]
    return None


def connect_wifi(
    ssid: str, password: str, iface: str | None = None, timeout: float = DEFAULT_CONNECT_TIMEOUT
) -> tuple[bool, str]:
    """Connect to a Wi-Fi access point using nmcli."""
    if not ssid or not ssid.strip():
        return False, "SSID cannot be empty."
    clean_ssid = ssid.strip()
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        SIMULATION_STATE["active_ssid"] = clean_ssid
        SIMULATION_STATE["hotspot_active"] = False
        return True, f"Connected to '{clean_ssid}' (simulated)."

    interface = iface or get_wifi_interface()
    args = ["device", "wifi", "connect", clean_ssid, "ifname", interface]
    if password:
        args += ["password", password]

    logger.info("Attempting nmcli connection to SSID '%s' on %s", clean_ssid, interface)
    code, out = run_nmcli(args, timeout=timeout)
    if code == 0:
        return True, f"Successfully connected to Wi-Fi: '{clean_ssid}'."
    return False, f"nmcli error ({code}): {out or 'Connection failed'}"


def disconnect_wifi(iface: str | None = None) -> bool:
    """Disconnect active wireless connection on interface."""
    interface = iface or get_wifi_interface()
    code, _ = run_nmcli(["device", "disconnect", interface])
    return code == 0
