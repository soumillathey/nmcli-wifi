"""hotspot.py — Manages the emergency Wi-Fi hotspot AP via nmcli."""
from __future__ import annotations

import logging

from wifi_nmcli.core.constants import DEFAULT_HOTSPOT_PASS, DEFAULT_HOTSPOT_SSID, HOTSPOT_CON_NAME
from wifi_nmcli.nmcli.ip import get_hotspot_ip
from wifi_nmcli.nmcli.runner import SIMULATION_STATE, get_wifi_interface, is_nmcli_available, run_nmcli

logger = logging.getLogger(__name__)


def is_hotspot_active(con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Check if emergency hotspot is currently active."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        return bool(SIMULATION_STATE.get("hotspot_active", False))
    code, out = run_nmcli(["-t", "-f", "NAME", "connection", "show", "--active"])
    return code == 0 and any(line.strip() == con_name for line in out.splitlines())


def start_hotspot(ssid: str = DEFAULT_HOTSPOT_SSID, password: str = DEFAULT_HOTSPOT_PASS, iface: str | None = None, con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Initiates an Access Point (Hotspot) on the wireless interface."""
    if is_hotspot_active(con_name): return True
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        SIMULATION_STATE["hotspot_active"] = True
        return True

    interface = iface or get_wifi_interface()
    run_nmcli(["connection", "delete", con_name])
    code, out = run_nmcli(["device", "wifi", "hotspot", "ifname", interface, "con-name", con_name, "ssid", ssid, "password", password])
    if code != 0:
        run_nmcli(["connection", "add", "type", "wifi", "ifname", interface, "con-name", con_name, "autoconnect", "no", "ssid", ssid])
        run_nmcli(["connection", "modify", con_name, "802-11-wireless.mode", "ap", "ipv4.method", "shared", "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password])
        code, out = run_nmcli(["connection", "up", con_name])
    logger.info("Hotspot '%s' activation returned code %d: %s", ssid, code, out)
    return code == 0


def stop_hotspot(con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Tears down the emergency hotspot connection."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        SIMULATION_STATE["hotspot_active"] = False
        return True
    code, _ = run_nmcli(["connection", "down", con_name])
    run_nmcli(["connection", "delete", con_name])
    return code == 0


__all__ = ["get_hotspot_ip", "is_hotspot_active", "start_hotspot", "stop_hotspot"]
