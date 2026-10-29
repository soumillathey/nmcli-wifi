"""monitor.py — Flap-debounced watchdog supervising Wi-Fi & hotspot failover."""
from __future__ import annotations

import logging
import threading

from wifi_nmcli.core.constants import DEFAULT_FAILURE_THRESHOLD, DEFAULT_WATCHDOG_INTERVAL
from wifi_nmcli.nmcli.hotspot import get_hotspot_ip, is_hotspot_active, start_hotspot, stop_hotspot
from wifi_nmcli.portal.service import portal_service
from wifi_nmcli.watchdog.connectivity import is_network_connected

logger = logging.getLogger(__name__)
_watchdog_thread: threading.Thread | None = None
_stop_event, _lock = threading.Event(), threading.RLock()


def _handle_status(online: bool, failures: int, threshold: int = DEFAULT_FAILURE_THRESHOLD) -> int:
    if online:
        if is_hotspot_active() or portal_service.is_running():
            logger.info("[Watchdog] Connectivity verified. Disabling emergency hotspot & portal.")
            stop_hotspot(); portal_service.stop()
        return 0
    if (failures := failures + 1) >= threshold and not is_hotspot_active():
        logger.warning("[Watchdog] Wi-Fi lost. Activating nmcli hotspot & captive portal...")
        if start_hotspot(): portal_service.start(ip=get_hotspot_ip())
        return 0
    return failures


def _loop(interval: float) -> None:
    failures = 0
    while not _stop_event.is_set():
        if not is_hotspot_active():
            failures = _handle_status(is_network_connected(), failures)
        _stop_event.wait(interval)


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
