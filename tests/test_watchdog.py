"""test_watchdog.py — Unit tests for Wi-Fi watchdog thread and debouncing."""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from wifi_nmcli.nmcli.runner import SIMULATION_STATE
from wifi_nmcli.watchdog import _handle_status, start_wifi_watchdog, stop_wifi_watchdog
from wifi_nmcli.watchdog.connectivity import is_network_connected


class TestWatchdog(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True
        SIMULATION_STATE["active_ssid"] = ""
        SIMULATION_STATE["hotspot_active"] = False

    def tearDown(self) -> None:
        stop_wifi_watchdog()

    @patch("socket.create_connection")
    def test_is_network_connected_success(self, mock_conn: MagicMock) -> None:
        mock_conn.return_value.__enter__.return_value = MagicMock()
        SIMULATION_STATE["enabled"] = False
        self.assertTrue(is_network_connected())

    @patch("socket.create_connection", side_effect=OSError("Unreachable"))
    def test_is_network_connected_failure(self, mock_conn: MagicMock) -> None:
        SIMULATION_STATE["enabled"] = False
        self.assertFalse(is_network_connected())

    def test_debounced_status_handling(self) -> None:
        # 1st failure below threshold=2 should return 1
        failures = _handle_status(online=False, failures=0, threshold=2)
        self.assertEqual(failures, 1)

        # 2nd failure reaches threshold, should trigger hotspot and reset failures to 0
        failures = _handle_status(online=False, failures=1, threshold=2)
        self.assertEqual(failures, 0)
        self.assertTrue(SIMULATION_STATE["hotspot_active"])

        # Online recovery should reset failures to 0 and disable hotspot
        failures = _handle_status(online=True, failures=5, threshold=2)
        self.assertEqual(failures, 0)
        self.assertFalse(SIMULATION_STATE["hotspot_active"])

    def test_watchdog_thread_lifecycle(self) -> None:
        start_wifi_watchdog(interval=0.1)
        stop_wifi_watchdog()


if __name__ == "__main__":
    unittest.main()
