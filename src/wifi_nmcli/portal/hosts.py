"""hosts.py — Ensures hermes.local is mapped in /etc/hosts for local Pi access."""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)
DEFAULT_HOSTS = Path("/etc/hosts")


def ensure_local_domain(domain: str = "hermes.local", ips: tuple[str, ...] = ("127.0.0.1", "10.42.0.1"), hosts_path: Path = DEFAULT_HOSTS) -> bool:
    """Ensure hermes.local points to loopback and hotspot gateway in /etc/hosts."""
    try:
        if not hosts_path.exists() or not hosts_path.is_file(): return False
        content = hosts_path.read_text(encoding="utf-8")
        needed = [f"{ip}\t{domain}" for ip in ips if f"{ip}\t{domain}" not in content and f"{ip} {domain}" not in content]
        if not needed: return True
        lines = [line for line in content.splitlines() if line.strip()]
        lines.extend(needed)
        hosts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info("[Hosts] Configured %s in %s: %s", domain, hosts_path, ", ".join(ips))
        return True
    except (OSError, PermissionError) as e:
        logger.warning("[Hosts] Cannot update %s: %s", hosts_path, e)
        return False
