"""wifi_setup.py — Standalone entrypoint for Hermes nmcli Wi-Fi setup."""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure local package resolution
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from wifi_nmcli.cli import main

if __name__ == "__main__":
    main()
