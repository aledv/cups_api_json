"""Tests for app.py with a fake `cups` module, so no CUPS server or pycups build is needed."""

import sys
import types
import unittest
from pathlib import Path
from unittest import mock

fake_cups = types.ModuleType("cups")
fake_cups.setServer = mock.Mock()
fake_cups.Connection = mock.Mock()
sys.modules["cups"] = fake_cups
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app  # noqa: E402


def connection(default="Office", state=3, pending=2, completed=5):
    conn = mock.Mock()
    conn.getDefault.return_value = default
    conn.getPrinters.return_value = {"Office": {"printer-state": state}}
    conn.getJobs.side_effect = lambda which_jobs, **kw: dict.fromkeys(
        range(pending if which_jobs == "not-completed" else completed)
    )
    return conn


class CupsStatusTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        fake_cups.Connection.reset_mock(side_effect=True, return_value=True)
        fake_cups.setServer.reset_mock()

    def test_status(self):
        fake_cups.Connection.return_value = connection()
        resp = self.client.get("/cups/status")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.get_json(),
            {"default_printer": "Office", "completed_jobs_count": 5, "pending_jobs_count": 2, "printer_status": "idle"},
        )

    def test_printer_states(self):
        for state, name in [(4, "processing"), (5, "stopped"), (9, "unknown")]:
            fake_cups.Connection.return_value = connection(state=state)
            self.assertEqual(self.client.get("/cups/status").get_json()["printer_status"], name)

    def test_no_default_or_missing_printer(self):
        fake_cups.Connection.return_value = connection(default=None)
        self.assertEqual(self.client.get("/cups/status").get_json()["printer_status"], "unknown")
        fake_cups.Connection.return_value = connection(default="Gone")
        self.assertEqual(self.client.get("/cups/status").get_json()["printer_status"], "not_found")

    def test_cups_down_hides_details(self):
        fake_cups.Connection.side_effect = RuntimeError("secret internal detail")
        with self.assertLogs("cups-api", level="ERROR"):
            resp = self.client.get("/cups/status")
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.get_json()["printer_status"], "error")
        self.assertNotIn("secret", resp.get_data(as_text=True))

    def test_cups_server_env(self):
        fake_cups.Connection.return_value = connection()
        with mock.patch.dict("os.environ", {"CUPS_SERVER": "printhost:631"}):
            self.client.get("/cups/status")
        fake_cups.setServer.assert_called_once_with("printhost:631")

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual((resp.status_code, resp.get_json()), (200, {"status": "healthy"}))


if __name__ == "__main__":
    unittest.main()
