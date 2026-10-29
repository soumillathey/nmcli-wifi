"""test_nmcli.py — Unit tests for nmcli scanner, connection, and hotspot."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from wifi_nmcli.core.vault import (
    delete_network,
    get_password,
    list_saved_networks,
    save_network,
)
from wifi_nmcli.nmcli.connection import (
    connect_wifi,
    get_active_wifi_ssid,
)
from wifi_nmcli.nmcli.hotspot import (
    is_hotspot_active,
    start_hotspot,
    stop_hotspot,
)
from wifi_nmcli.nmcli.runner import (
    SIMULATION_STATE,
    get_wifi_interface,
)
from wifi_nmcli.nmcli.scanner import _parse_nmcli_line, scan_networks


class TestNmcliComponents(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True
        SIMULATION_STATE["active_ssid"] = ""
        SIMULATION_STATE["hotspot_active"] = False

    def test_parse_nmcli_line(self) -> None:
        line = "*:Office\\:5G:80:WPA2:▂▄▆█"
        parsed = _parse_nmcli_line(line)
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed["ssid"], "Office:5G")
        self.assertEqual(parsed["signal"], 80)
        self.assertTrue(parsed["in_use"])

    def test_scan_networks_simulated(self) -> None:
        nets = scan_networks()
        self.assertGreater(len(nets), 0)
        self.assertIn("ssid", nets[0])

    def test_connect_wifi_empty(self) -> None:
        ok, msg = connect_wifi("", "12345678")
        self.assertFalse(ok)
        self.assertIn("cannot be empty", msg)

    def test_connect_wifi_simulated(self) -> None:
        ok, _msg = connect_wifi("TestNet", "pass123")
        self.assertTrue(ok)
        self.assertEqual(get_active_wifi_ssid(), "TestNet")

    def test_hotspot_lifecycle_simulated(self) -> None:
        self.assertFalse(is_hotspot_active())
        self.assertTrue(start_hotspot("hermes", "12345678"))
        self.assertTrue(is_hotspot_active())
        self.assertTrue(stop_hotspot())
        self.assertFalse(is_hotspot_active())

    def test_vault_operations(self) -> None:
        save_network("MyOffice", "Secret99")
        self.assertEqual(get_password("MyOffice"), "Secret99")
        saved = list_saved_networks()
        self.assertTrue(any(s["ssid"] == "MyOffice" for s in saved))
        self.assertTrue(delete_network("MyOffice"))
        self.assertIsNone(get_password("MyOffice"))

    def test_interface_fallback(self) -> None:
        with patch("pathlib.Path.is_dir", return_value=False):
            self.assertEqual(get_wifi_interface(), "wlan0")


if __name__ == "__main__":
    unittest.main()
