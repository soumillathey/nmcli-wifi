"""runner.py — Low-level nmcli command executor and interface detection."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from wifi_nmcli.nmcli.activity import nmcli_lock

SIMULATION_STATE: dict[str, Any] = {
    "enabled": False, "active_ssid": "", "hotspot_active": False, "scan_results": [],
}


def is_nmcli_available() -> bool:
    """Checks whether the nmcli binary is present on the system."""
    return shutil.which("nmcli") is not None


def get_wifi_interface() -> str:
    """Detect the first wireless interface on the system or default to wlan0."""
    sys_net = Path("/sys/class/net")
    if sys_net.is_dir():
        for dev in sys_net.iterdir():
            if (dev / "wireless").is_dir() or dev.name.startswith("wl"):
                return dev.name
    return "wlan0"


def run_nmcli(args: list[str], timeout: float = 15.0, cooldown: float = 0.0) -> tuple[int, str]:
    """Execute an nmcli command serialized with optional watchdog suspension."""
    if not is_nmcli_available() or SIMULATION_STATE["enabled"]:
        return 0, ""
    pfx = ["sudo", "-n"] if getattr(os, "geteuid", lambda: 0)() != 0 and shutil.which("sudo") else []
    with nmcli_lock(cooldown=cooldown):
        try:
            proc = subprocess.run(
                pfx + ["nmcli"] + args,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return proc.returncode, (proc.stdout or proc.stderr).strip()
        except (subprocess.SubprocessError, OSError) as e:
            return 1, str(e)
