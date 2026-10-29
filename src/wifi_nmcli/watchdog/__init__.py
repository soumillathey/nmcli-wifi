"""watchdog subpackage exports."""
from wifi_nmcli.watchdog.connectivity import is_network_connected
from wifi_nmcli.watchdog.monitor import (
    _handle_status,
    _loop,
    start_wifi_watchdog,
    stop_wifi_watchdog,
)

__all__ = [
    "_handle_status",
    "_loop",
    "is_network_connected",
    "start_wifi_watchdog",
    "stop_wifi_watchdog",
]
