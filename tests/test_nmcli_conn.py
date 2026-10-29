"""test_nmcli_conn.py — Unit tests for nmcli Wi-Fi connection and hotspot lifecycle."""
from __future__ import annotations

import unittest

from wifi_nmcli.nmcli.connection import connect_wifi, get_active_wifi_ssid
from wifi_nmcli.nmcli.hotspot import is_hotspot_active, start_hotspot, stop_hotspot
from wifi_nmcli.nmcli.runner import SIMULATION_STATE


class TestNmcliConnection(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True
        SIMULATION_STATE["active_ssid"] = ""
        SIMULATION_STATE["hotspot_active"] = False

    def test_connect_wifi_empty(self) -> None:
        ok, msg = connect_wifi("", "12345678")
        self.assertFalse(ok); self.assertIn("cannot be empty", msg)

    def test_connect_wifi_simulated(self) -> None:
        ok, _msg = connect_wifi("TestNet", "pass123")
        self.assertTrue(ok); self.assertEqual(get_active_wifi_ssid(), "TestNet")

    def test_hotspot_lifecycle_simulated(self) -> None:
        self.assertFalse(is_hotspot_active())
        self.assertTrue(start_hotspot("hermes", "12345678"))
        self.assertTrue(is_hotspot_active())
        self.assertTrue(stop_hotspot())
        self.assertFalse(is_hotspot_active())


if __name__ == "__main__":
    unittest.main()
