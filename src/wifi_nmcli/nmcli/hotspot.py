"""hotspot.py — Manages the emergency Wi-Fi hotspot AP via nmcli."""
from __future__ import annotations

import logging

from wifi_nmcli.core.constants import DEFAULT_HOTSPOT_PASS, DEFAULT_HOTSPOT_SSID, HOTSPOT_CON_NAME
from wifi_nmcli.nmcli.activity import suspend_watchdog
from wifi_nmcli.nmcli.ip import get_hotspot_ip
from wifi_nmcli.nmcli.runner import SIMULATION_STATE, get_wifi_interface, is_nmcli_available, run_nmcli

logger = logging.getLogger(__name__)
_hotspot_active = False


def is_hotspot_active(con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Check if emergency hotspot is currently active."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        return bool(SIMULATION_STATE.get("hotspot_active", _hotspot_active))
    return _hotspot_active


def start_hotspot(ssid: str = DEFAULT_HOTSPOT_SSID, password: str = DEFAULT_HOTSPOT_PASS, iface: str | None = None, con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Initiates an Access Point (Hotspot) on the wireless interface."""
    global _hotspot_active
    if _hotspot_active: return True
    suspend_watchdog(10.0)
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        _hotspot_active = SIMULATION_STATE["hotspot_active"] = True
        return True

    dev = iface or get_wifi_interface()
    logger.info("[WiFi] Creating emergency hotspot '%s' on %s...", ssid, dev)
    run_nmcli(["connection", "delete", con_name])
    run_nmcli(["connection", "add", "type", "wifi", "ifname", dev, "con-name", con_name, "autoconnect", "no", "ssid", ssid])
    run_nmcli(["connection", "modify", con_name, "802-11-wireless.mode", "ap", "802-11-wireless.band", "bg", "ipv4.method", "shared", "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password])
    code, out = run_nmcli(["connection", "up", con_name])
    if code != 0:
        logger.warning("[WiFi] Profile failed (%s), trying hotspot shortcut...", out)
        code, out = run_nmcli(["device", "wifi", "hotspot", "ifname", dev, "con-name", con_name, "ssid", ssid, "password", password])

    _hotspot_active = (code == 0)
    suspend_watchdog(10.0)
    msg = f"Hotspot AP '{ssid}' active! IP: {get_hotspot_ip(dev)}" if _hotspot_active else f"Hotspot failed (code {code}): {out}"
    (logger.info if _hotspot_active else logger.error)(f"[WiFi] {msg}")
    return _hotspot_active


def stop_hotspot(con_name: str = HOTSPOT_CON_NAME) -> bool:
    """Tears down the emergency hotspot connection."""
    global _hotspot_active
    suspend_watchdog(10.0); _hotspot_active = False
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        SIMULATION_STATE["hotspot_active"] = False
        return True
    code, _ = run_nmcli(["connection", "down", con_name])
    run_nmcli(["connection", "delete", con_name])
    return code == 0


__all__ = ["get_hotspot_ip", "is_hotspot_active", "start_hotspot", "stop_hotspot"]
