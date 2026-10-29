"""redirect.py — Port 80 cleanup and iptables redirection for captive portal."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time

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
        _run_cmd(["fuser", "-k", "-9", f"{port}/tcp"])
    for proc_name in ("wifi-connect",):
        _run_cmd(["pkill", "-9", "-f", proc_name])
    time.sleep(0.05)


def setup_port_forwarding(iface: str = "wlan0", from_port: int = 80, to_port: int = 8080) -> bool:
    """Redirect client PREROUTING and local OUTPUT traffic to to_port."""
    if not shutil.which("iptables"): return False
    teardown_port_forwarding(iface, from_port, to_port)
    p = str(from_port); t = str(to_port)
    _run_cmd(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
    _run_cmd(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "-o", "lo", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
    _run_cmd(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "-d", "10.42.0.1", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
    logger.info("[Redirect] iptables PREROUTING & OUTPUT active: :%s -> :%s", p, t)
    return True


def teardown_port_forwarding(iface: str = "wlan0", from_port: int = 80, to_port: int = 8080) -> None:
    """Remove active iptables PREROUTING and OUTPUT redirection rules."""
    if not shutil.which("iptables"): return
    p = str(from_port); t = str(to_port)
    _run_cmd(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
    _run_cmd(["iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "-o", "lo", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
    _run_cmd(["iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "-d", "10.42.0.1", "--dport", p, "-j", "REDIRECT", "--to-ports", t])
