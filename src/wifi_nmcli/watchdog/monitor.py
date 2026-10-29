"""monitor.py — Flap-debounced watchdog supervising Wi-Fi & hotspot failover."""
from __future__ import annotations

import logging
import threading

from wifi_nmcli.core.constants import DEFAULT_FAILURE_THRESHOLD
from wifi_nmcli.nmcli.hotspot import get_hotspot_ip, is_hotspot_active, start_hotspot, stop_hotspot
from wifi_nmcli.portal.service import portal_service
from wifi_nmcli.watchdog.connectivity import is_network_connected

logger = logging.getLogger(__name__)
_stop_event = threading.Event()


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
