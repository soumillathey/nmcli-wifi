"""constants.py — Default configuration constants for nmcli-based Wi-Fi setup."""
from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "portal" / "templates"
DATA_DIR = BASE_DIR.parents[1] / "data"
VAULT_DB_PATH = DATA_DIR / "wifi_vault.db"

DEFAULT_HOTSPOT_SSID = "hermes"
DEFAULT_HOTSPOT_PASS = "12345678"
HOTSPOT_CON_NAME = "hermes-hotspot"

DEFAULT_GATEWAY_IP = "10.42.0.1"
FALLBACK_GATEWAY_IP = "192.168.42.1"
DEFAULT_PORTAL_PORT = 80
DEFAULT_DNS_PORT = 53

DEFAULT_WATCHDOG_INTERVAL = 1.0
DEFAULT_FAILURE_THRESHOLD = 2
DEFAULT_CONNECT_TIMEOUT = 30.0
