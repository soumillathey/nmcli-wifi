"""scanner.py — Discovers available wireless networks via nmcli."""
from __future__ import annotations

from typing import Any

from wifi_nmcli.nmcli.runner import (
    SIMULATION_STATE,
    get_wifi_interface,
    is_nmcli_available,
    run_nmcli,
)

_DEFAULT_SIMULATED = [
    {"ssid": "Office_WiFi_5G", "signal": 85, "security": "WPA2", "bars": "▂▄▆█"},
    {"ssid": "Factory_Guest", "signal": 60, "security": "Open", "bars": "▂▄▆_"},
    {"ssid": "Warehouse_AP_North", "signal": 45, "security": "WPA2", "bars": "▂▄__"},
    {"ssid": "MobileHotspot", "signal": 95, "security": "WPA2", "bars": "▂▄▆█"},
]


def _parse_nmcli_line(line: str) -> dict[str, Any] | None:
    parts = line.replace(r"\:", "__COLON__").split(":")
    if len(parts) < 4:
        return None
    in_use, raw_ssid, raw_sig, raw_sec = parts[0], parts[1], parts[2], parts[3]
    ssid = raw_ssid.replace("__COLON__", ":").strip()
    if not ssid or ssid == "--":
        return None
    try:
        signal = int(raw_sig)
    except ValueError:
        signal = 0
    return {
        "ssid": ssid,
        "signal": signal,
        "security": raw_sec.replace("__COLON__", ":").strip() or "Open",
        "in_use": in_use.strip() == "*",
        "bars": parts[4].strip() if len(parts) > 4 else "",
    }


def scan_networks(iface: str | None = None) -> list[dict[str, Any]]:
    """Scan and return unique Wi-Fi access points sorted by signal strength."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        return SIMULATION_STATE.get("scan_results") or list(_DEFAULT_SIMULATED)

    interface = iface or get_wifi_interface()
    code, out = run_nmcli(["-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY,BARS", "device", "wifi", "list", "ifname", interface, "--rescan", "yes"])
    if code != 0:
        code, out = run_nmcli(["-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY,BARS", "device", "wifi", "list"])

    seen: dict[str, dict[str, Any]] = {}
    for line in out.splitlines():
        if (item := _parse_nmcli_line(line.strip())) and (item["ssid"] not in seen or item["signal"] > seen[item["ssid"]]["signal"]):
            seen[item["ssid"]] = item
    return sorted(seen.values(), key=lambda x: int(x["signal"]), reverse=True)
