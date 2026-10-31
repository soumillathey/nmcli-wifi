"""capport.py — Configures NetworkManager dnsmasq for DHCP Option 114 and wildcard DNS."""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)
NM_DNSMASQ_DIR = Path("/etc/NetworkManager/dnsmasq-shared.d")
NM_CAPPORT_FILE = NM_DNSMASQ_DIR / "hermes-captive.conf"


def setup_nm_capport_config(gateway_ip: str = "10.42.0.1") -> bool:
    """Configures NetworkManager shared dnsmasq for wildcard DNS and RFC 8910 Option 114."""
    try:
        content = (
            f"address=/#/{gateway_ip}\n"
            f"address=/=/{gateway_ip}\n"
            f"dhcp-option=114,http://{gateway_ip}/.well-known/captive-portal\n"
        )
        if NM_CAPPORT_FILE.exists() and NM_CAPPORT_FILE.read_text(encoding="utf-8") == content:
            return True
        pfx = ["sudo", "-n"] if shutil.which("sudo") else []
        subprocess.run(pfx + ["mkdir", "-p", str(NM_DNSMASQ_DIR)], check=False)
        cmd = pfx + ["tee", str(NM_CAPPORT_FILE)]
        proc = subprocess.run(cmd, input=content.encode("utf-8"), capture_output=True, check=False)
        if proc.returncode == 0:
            logger.info("[Capport] Installed DHCP Option 114 and wildcard DNS in %s", NM_CAPPORT_FILE)
            return True
    except (subprocess.SubprocessError, OSError) as e:
        logger.warning("[Capport] Unable to configure %s: %s", NM_CAPPORT_FILE, e)
    return False


def teardown_nm_capport_config() -> None:
    """Removes custom NetworkManager dnsmasq configuration."""
    try:
        if NM_CAPPORT_FILE.exists():
            pfx = ["sudo", "-n"] if shutil.which("sudo") else []
            subprocess.run(pfx + ["rm", "-f", str(NM_CAPPORT_FILE)], check=False)
    except (subprocess.SubprocessError, OSError): pass


__all__ = ["setup_nm_capport_config", "teardown_nm_capport_config"]
