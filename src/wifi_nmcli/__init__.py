"""wifi_nmcli package — Pure nmcli-based Wi-Fi manager with watchdog & captive portal."""
from wifi_nmcli.core import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_GATEWAY_IP,
    DEFAULT_HOTSPOT_PASS,
    DEFAULT_HOTSPOT_SSID,
    HOTSPOT_CON_NAME,
    delete_network,
    get_password,
    list_saved_networks,
    save_network,
)
from wifi_nmcli.nmcli import (
    SIMULATION_STATE,
    connect_wifi,
    disconnect_wifi,
    get_active_wifi_ssid,
    get_hotspot_ip,
    get_wifi_interface,
    is_hotspot_active,
    is_nmcli_available,
    is_nmcli_busy,
    is_watchdog_suspended,
    scan_networks,
    start_hotspot,
    stop_hotspot,
    suspend_watchdog,
)
from wifi_nmcli.portal import CaptiveDNSServer, CaptiveHTTPServer, PortalService, portal_service
from wifi_nmcli.watchdog import is_network_connected, start_wifi_watchdog, stop_wifi_watchdog

__all__ = [
    "DEFAULT_CONNECT_TIMEOUT", "DEFAULT_GATEWAY_IP", "DEFAULT_HOTSPOT_PASS", "DEFAULT_HOTSPOT_SSID",
    "HOTSPOT_CON_NAME", "SIMULATION_STATE", "CaptiveDNSServer", "CaptiveHTTPServer", "PortalService",
    "connect_wifi", "delete_network", "disconnect_wifi", "get_active_wifi_ssid", "get_hotspot_ip",
    "get_password", "get_wifi_interface", "is_hotspot_active", "is_network_connected",
    "is_nmcli_available", "is_nmcli_busy", "is_watchdog_suspended", "list_saved_networks",
    "portal_service", "save_network", "scan_networks", "start_hotspot", "start_wifi_watchdog",
    "stop_hotspot", "stop_wifi_watchdog", "suspend_watchdog",
]
