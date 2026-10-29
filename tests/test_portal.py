"""test_portal.py — Unit tests for captive DNS server and HTTP endpoints."""
from __future__ import annotations

import json
import socket
import unittest
import urllib.request
from unittest.mock import patch

from wifi_nmcli.nmcli.runner import SIMULATION_STATE
from wifi_nmcli.portal.dns_server import _build_response
from wifi_nmcli.portal.http_server import CaptiveHTTPServer
from wifi_nmcli.portal.redirect import kill_stale_portal_listeners, setup_port_forwarding, teardown_port_forwarding
from wifi_nmcli.portal.service import portal_service


class TestCaptivePortal(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True

    def test_dns_packet_builder(self) -> None:
        dummy = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        resp = _build_response(dummy, "10.42.0.1")
        self.assertEqual(resp[:2], b"\x12\x34"); self.assertTrue(resp.endswith(socket.inet_aton("10.42.0.1")))

    def test_http_server_endpoints(self) -> None:
        http_srv = CaptiveHTTPServer(port=8899)
        self.assertTrue(http_srv.start())
        try:
            base = f"http://127.0.0.1:{http_srv.port}"
            with urllib.request.urlopen(f"{base}/", timeout=3.0) as r:
                self.assertEqual(r.status, 200); self.assertIn("Gluvok Hermes", r.read().decode("utf-8"))
            with urllib.request.urlopen(f"{base}/networks", timeout=3.0) as r:
                self.assertEqual(r.status, 200); self.assertIsInstance(json.loads(r.read().decode("utf-8")), list)
            payload = json.dumps({"ssid": "OfficePortalTest", "password": "pass"}).encode("utf-8")
            req = urllib.request.Request(f"{base}/connect", data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=3.0) as r:
                self.assertEqual(r.status, 200); self.assertTrue(json.loads(r.read().decode("utf-8"))["success"])
        finally:
            http_srv.stop()

    def test_portal_service_lifecycle(self) -> None:
        self.assertFalse(portal_service.is_running())
        portal_service.start(http_port=8898, dns_port=5553)
        self.assertTrue(portal_service.is_running()); portal_service.stop()
        self.assertFalse(portal_service.is_running())

    @patch("shutil.which", return_value="/sbin/iptables")
    @patch("wifi_nmcli.portal.redirect._run_cmd", return_value=True)
    def test_redirect_utilities(self, mock_cmd: patch, mock_which: patch) -> None:
        self.assertTrue(setup_port_forwarding("wlan0", 80, 8080))
        teardown_port_forwarding("wlan0", 80, 8080); kill_stale_portal_listeners(80)


if __name__ == "__main__":
    unittest.main()
