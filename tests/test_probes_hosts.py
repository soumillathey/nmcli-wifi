"""test_probes_hosts.py — Unit tests for captive portal probe redirect and hosts file."""
from __future__ import annotations

import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from wifi_nmcli.nmcli.runner import SIMULATION_STATE
from wifi_nmcli.portal.hosts import ensure_local_domain
from wifi_nmcli.portal.http_server import CaptiveHTTPServer


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: urllib.request.Request, fp: object, code: int, msg: str, headers: object, newurl: str) -> None:
        return None


class TestProbesAndHosts(unittest.TestCase):
    def setUp(self) -> None:
        SIMULATION_STATE["enabled"] = True

    def test_ensure_local_domain(self) -> None:
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("127.0.0.1 localhost\n"); p = Path(f.name)
        try:
            self.assertTrue(ensure_local_domain("hermes.local", ("127.0.0.1", "10.42.0.1"), hosts_path=p))
            txt = p.read_text()
            self.assertIn("127.0.0.1\thermes.local", txt); self.assertIn("10.42.0.1\thermes.local", txt)
            self.assertTrue(ensure_local_domain("hermes.local", ("127.0.0.1", "10.42.0.1"), hosts_path=p))
        finally:
            p.unlink(missing_ok=True)

    def test_captive_probe_and_external_host_redirect(self) -> None:
        http_srv = CaptiveHTTPServer(port=8896)
        self.assertTrue(http_srv.start())
        opener = urllib.request.build_opener(NoRedirectHandler)
        try:
            for path in ("/generate_204", "/hotspot-detect.html"):
                try: opener.open(f"http://127.0.0.1:{http_srv.port}{path}", timeout=3.0)
                except urllib.error.HTTPError as e:
                    self.assertEqual(e.code, 302); self.assertEqual(e.headers.get("Location"), "http://10.42.0.1/")

            req = urllib.request.Request(f"http://127.0.0.1:{http_srv.port}/some/path", headers={"Host": "connectivitycheck.gstatic.com"})
            try: opener.open(req, timeout=3.0)
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 302); self.assertEqual(e.headers.get("Location"), "http://10.42.0.1/")
        finally:
            http_srv.stop()


if __name__ == "__main__":
    unittest.main()
