"""lifecycle.py — Thread-safe control of the Wi-Fi watchdog thread."""
from __future__ import annotations

import threading

from wifi_nmcli.core.constants import DEFAULT_WATCHDOG_INTERVAL
from wifi_nmcli.watchdog.monitor import _loop, _stop_event

_watchdog_thread: threading.Thread | None = None
_lock = threading.RLock()


def start_wifi_watchdog(interval: float = DEFAULT_WATCHDOG_INTERVAL) -> None:
    """Start background watchdog thread."""
    global _watchdog_thread
    with _lock:
        if not (_watchdog_thread and _watchdog_thread.is_alive()):
            _stop_event.clear()
            _watchdog_thread = threading.Thread(target=_loop, args=(interval,), name="WiFiWatchdog", daemon=True)
            _watchdog_thread.start()


def stop_wifi_watchdog(timeout: float = 3.0) -> None:
    """Stop background watchdog thread."""
    global _watchdog_thread
    with _lock:
        _stop_event.set()
        if _watchdog_thread and _watchdog_thread.is_alive():
            _watchdog_thread.join(timeout=timeout)
        _watchdog_thread = None
