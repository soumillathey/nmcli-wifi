"""test_nmcli.py — Unit tests for nmcli scanner, vault, and interface detection."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from wifi_nmcli.core.vault import delete_network, get_password, list_saved_networks, save_network
from wifi_nmcli.nmcli.runner import SIMULATION_STATE, get_wifi_interface
from wifi_nmcli.nmcli.scanner import _parse_nmcli_line, scan_networks


class TestNmcliBasic(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True

    def test_parse_nmcli_line(self) -> None:
        parsed = _parse_nmcli_line("*:Office\\:5G:80:WPA2:▂▄▆█")
        assert parsed is not None
        self.assertEqual(parsed["ssid"], "Office:5G"); self.assertEqual(parsed["signal"], 80); self.assertTrue(parsed["in_use"])

    def test_scan_networks_simulated(self) -> None:
        nets = scan_networks()
        self.assertGreater(len(nets), 0); self.assertIn("ssid", nets[0])

    def test_vault_operations(self) -> None:
        save_network("MyOffice", "Secret99")
        self.assertEqual(get_password("MyOffice"), "Secret99")
        self.assertTrue(any(s["ssid"] == "MyOffice" for s in list_saved_networks()))
        self.assertTrue(delete_network("MyOffice")); self.assertIsNone(get_password("MyOffice"))

    def test_interface_fallback(self) -> None:
        with patch("pathlib.Path.is_dir", return_value=False):
            self.assertEqual(get_wifi_interface(), "wlan0")


if __name__ == "__main__":
    unittest.main()
