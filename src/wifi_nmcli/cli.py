"""cli.py — Command-line interface for nmcli Wi-Fi watchdog & setup."""
from __future__ import annotations

import argparse
import signal
import sys
import time

from wifi_nmcli.core.constants import DEFAULT_HOTSPOT_PASS, DEFAULT_HOTSPOT_SSID
from wifi_nmcli.nmcli import connect_wifi, scan_networks, start_hotspot, stop_hotspot
from wifi_nmcli.portal import portal_service
from wifi_nmcli.watchdog import start_wifi_watchdog, stop_wifi_watchdog


def _shutdown(signum: int = 0, frame: object = None) -> None:
    print("\n[WiFi Setup] Shutting down watchdog and captive portal...")
    stop_wifi_watchdog()
    portal_service.stop()
    stop_hotspot()
    sys.exit(0)


def main() -> None:
    p = argparse.ArgumentParser(description="Hermes nmcli Wi-Fi Setup & Watchdog")
    p.add_argument("--scan", action="store_true", help="Scan nearby Wi-Fi networks")
    p.add_argument("--connect", action="store_true", help="Connect to specified Wi-Fi")
    p.add_argument("--ssid", default="", help="Target network SSID")
    p.add_argument("--password", default="", help="Network password")
    p.add_argument("--hotspot", action="store_true", help="Manually activate emergency hotspot")
    args = p.parse_args()

    if args.scan:
        for net in scan_networks():
            print(f"- {net['ssid']} ({net.get('signal', 0)}%) [{net.get('security', 'Open')}]")
        return
    if args.connect:
        ssid = args.ssid or input("SSID: ")
        pwd = args.password or input("Password: ")
        ok, msg = connect_wifi(ssid, pwd)
        print(f"[{'SUCCESS' if ok else 'FAILED'}] {msg}")
        return

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    if args.hotspot:
        start_hotspot(args.ssid or DEFAULT_HOTSPOT_SSID, args.password or DEFAULT_HOTSPOT_PASS)
        portal_service.start()
        print(f"[WiFi Setup] Hotspot active (SSID: {args.ssid or DEFAULT_HOTSPOT_SSID}). Press Ctrl+C to stop.")

    start_wifi_watchdog()
    print("[WiFi Setup] Watchdog active. Monitoring Wi-Fi connectivity...")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        _shutdown()
