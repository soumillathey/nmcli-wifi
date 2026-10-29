"""nmcli subpackage exports."""
from wifi_nmcli.nmcli.connection import (
    connect_wifi,
    disconnect_wifi,
    get_active_wifi_ssid,
)
from wifi_nmcli.nmcli.hotspot import (
    get_hotspot_ip,
    is_hotspot_active,
    start_hotspot,
    stop_hotspot,
)
from wifi_nmcli.nmcli.runner import (
    SIMULATION_STATE,
    get_wifi_interface,
    is_nmcli_available,
    run_nmcli,
)
from wifi_nmcli.nmcli.scanner import scan_networks

__all__ = [
    "SIMULATION_STATE",
    "connect_wifi",
    "disconnect_wifi",
    "get_active_wifi_ssid",
    "get_hotspot_ip",
    "get_wifi_interface",
    "is_hotspot_active",
    "is_nmcli_available",
    "run_nmcli",
    "scan_networks",
    "start_hotspot",
    "stop_hotspot",
]
