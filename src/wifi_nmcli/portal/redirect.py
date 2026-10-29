"""redirect.py — Port 80 cleanup and iptables redirection for captive portal."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)


def _run_cmd(cmd: list[str]) -> bool:
    pfx = ["sudo", "-n"] if getattr(os, "geteuid", lambda: 0)() != 0 and shutil.which("sudo") else []
    try:
        res = subprocess.run(pfx + cmd, capture_output=True, timeout=2.0, check=False)
        return res.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def kill_stale_portal_listeners(port: int = 80) -> None:
    """Terminate orphaned wifi-connect or python processes on port."""
    if shutil.which("fuser"):
        _run_cmd(["fuser", "-k", f"{port}/tcp"])
    for proc_name in ("wifi-connect",):
        _run_cmd(["pkill", "-9", "-f", proc_name])


def setup_port_forwarding(iface: str = "wlan0", from_port: int = 80, to_port: int = 8080) -> bool:
    """Redirect incoming client traffic on from_port to to_port via iptables."""
    if not shutil.which("iptables"): return False
    teardown_port_forwarding(iface, from_port, to_port)
    cmd = ["iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", str(from_port), "-j", "REDIRECT", "--to-ports", str(to_port)]
    ok = _run_cmd(cmd)
    if ok: logger.info("[Redirect] iptables PREROUTING active: %s:%d -> :%d", iface, from_port, to_port)
    return ok


def teardown_port_forwarding(iface: str = "wlan0", from_port: int = 80, to_port: int = 8080) -> None:
    """Remove active iptables PREROUTING redirection rule."""
    if not shutil.which("iptables"): return
    cmd = ["iptables", "-t", "nat", "-D", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", str(from_port), "-j", "REDIRECT", "--to-ports", str(to_port)]
    _run_cmd(cmd)
