"""redirect.py — Port cleanup and iptables redirection for captive portal."""
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
    if shutil.which("fuser"): _run_cmd(["fuser", "-k", "-9", f"{port}/tcp"])
    for proc_name in ("wifi-connect",): _run_cmd(["pkill", "-9", "-f", proc_name])
    time.sleep(0.05)


def setup_port_forwarding(iface: str = "wlan0", http_port: int = 80, dns_port: int = 5353) -> bool:
    """Redirect client PREROUTING and local OUTPUT traffic."""
    if not shutil.which("iptables"): return False
    teardown_port_forwarding(iface, http_port, dns_port)
    hp, dp = str(http_port), str(dns_port)
    if http_port != 80:
        _run_cmd(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
        _run_cmd(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "-o", "lo", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
        _run_cmd(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "-d", "10.42.0.1", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
    _run_cmd(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "udp", "--dport", "53", "-j", "REDIRECT", "--to-ports", dp])
    _run_cmd(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "53", "-j", "REDIRECT", "--to-ports", dp])
    logger.info("[Redirect] iptables active: HTTP=%s, DNS :53 -> :%s", hp, dp)
    return True


def teardown_port_forwarding(iface: str = "wlan0", http_port: int = 80, dns_port: int = 5353) -> None:
    """Remove active iptables PREROUTING and OUTPUT redirection rules."""
    if not shutil.which("iptables"): return
    hp, dp = str(http_port), str(dns_port)
    _run_cmd(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
    _run_cmd(["iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "-o", "lo", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
    _run_cmd(["iptables", "-t", "nat", "-D", "OUTPUT", "-p", "tcp", "-d", "10.42.0.1", "--dport", "80", "-j", "REDIRECT", "--to-ports", hp])
    _run_cmd(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", iface, "-p", "udp", "--dport", "53", "-j", "REDIRECT", "--to-ports", dp])
    _run_cmd(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", iface, "-p", "tcp", "--dport", "53", "-j", "REDIRECT", "--to-ports", dp])
