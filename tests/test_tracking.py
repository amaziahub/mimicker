import time

import pytest
from hamcrest import assert_that, is_, has_length, has_entry, equal_to

from mimicker.mimicker import mimicker, get, post
from mimicker.tracking import RequestTracker
from tests.support.client import Client


# ── unit tests for RequestTracker ────────────────────────────────────────────

class TestRequestTracker:
    def setup_method(self):
        self.tracker = RequestTracker()

    def test_register_stub_appears_in_report(self):
        self.tracker.register_stub("GET", "/hello")
        report = self.tracker.report()
        assert_that(report["summary"]["total_stubs"], is_(1))
        assert_that(report["stubs"][0], has_entry("path", "/hello"))

    def test_hit_count_increments(self):
        self.tracker.register_stub("GET", "/hello")
        self.tracker.record_hit("GET", "/hello")
        self.tracker.record_hit("GET", "/hello")
        report = self.tracker.report()
        assert_that(report["stubs"][0]["hit_count"], is_(2))

    def test_unused_stub_appears_in_unused_list(self):
        self.tracker.register_stub("GET", "/never-called")
        report = self.tracker.report()
        assert_that(report["unused_stubs"], has_length(1))
        assert_that(report["unused_stubs"][0]["path"], is_("/never-called"))

    def test_hit_stub_not_in_unused_list(self):
        self.tracker.register_stub("GET", "/called")
        self.tracker.record_hit("GET", "/called")
        report = self.tracker.report()
        assert_that(report["unused_stubs"], has_length(0))

    def test_unmatched_request_recorded(self):
        self.tracker.record_unmatched("GET", "/unknown")
        report = self.tracker.report()
        assert_that(report["summary"]["unmatched_requests"], is_(1))
        assert_that(report["unmatched_requests"][0]["path"], is_("/unknown"))

    def test_reset_clears_hits_and_unmatched(self):
        self.tracker.register_stub("GET", "/stub")
        self.tracker.record_hit("GET", "/stub")
        self.tracker.record_unmatched("GET", "/unknown")
        self.tracker.reset()
        report = self.tracker.report()
        assert_that(report["stubs"][0]["hit_count"], is_(0))
        assert_that(report["summary"]["unmatched_requests"], is_(0))

    def test_summary_counts_are_correct(self):
        self.tracker.register_stub("GET", "/a")
        self.tracker.register_stub("GET", "/b")
        self.tracker.record_hit("GET", "/a")
        self.tracker.record_unmatched("POST", "/unknown")
        report = self.tracker.report()
        s = report["summary"]
        assert_that(s["total_stubs"], is_(2))
        assert_that(s["matched_stubs"], is_(1))
        assert_that(s["unmatched_requests"], is_(1))

    def test_unmatched_record_has_timestamp(self):
        self.tracker.record_unmatched("GET", "/oops")
        report = self.tracker.report()
        ts = report["unmatched_requests"][0]["timestamp"]
        assert ts.endswith("Z"), f"Expected ISO timestamp ending in Z, got: {ts}"

    def test_hit_unknown_stub_is_ignored(self):
        # Hitting a stub that was never registered should not crash
        self.tracker.record_hit("GET", "/not-registered")
        report = self.tracker.report()
        assert_that(report["summary"]["total_stubs"], is_(0))


# ── integration tests: tracking through the live server ──────────────────────

@pytest.fixture
def tracking_server():
    server = mimicker(port=0)
    yield server
    server.shutdown()


def test_server_report_endpoint_accessible(tracking_server):
    port = tracking_server.get_port()
    client = Client(f"http://localhost:{port}")
    resp = client.get("/__mimicker__/report")
    assert_that(resp.status_code, is_(200))
    assert "summary" in resp.json()


def test_matched_stub_increments_hit_count(tracking_server):
    port = tracking_server.get_port()
    tracking_server.routes(get("/track/hit").status(200).body({"ok": True}))
    client = Client(f"http://localhost:{port}")

    client.get("/track/hit")
    client.get("/track/hit")

    report = client.get("/__mimicker__/report").json()
    hit = next(s for s in report["stubs"] if s["path"] == "/track/hit")
    assert_that(hit["hit_count"], is_(2))


def test_unmatched_request_appears_in_report(tracking_server):
    port = tracking_server.get_port()
    client = Client(f"http://localhost:{port}")

    client.get("/track/does-not-exist-xyz")

    report = client.get("/__mimicker__/report").json()
    paths = [r["path"] for r in report["unmatched_requests"]]
    assert "/track/does-not-exist-xyz" in paths


def test_unused_stub_appears_in_report(tracking_server):
    port = tracking_server.get_port()
    tracking_server.routes(get("/track/unused").status(200))
    client = Client(f"http://localhost:{port}")

    report = client.get("/__mimicker__/report").json()
    unused_paths = [s["path"] for s in report["unused_stubs"]]
    assert "/track/unused" in unused_paths


def test_admin_endpoints_not_recorded_as_unmatched(tracking_server):
    port = tracking_server.get_port()
    client = Client(f"http://localhost:{port}")

    client.get("/__mimicker__/health")
    client.get("/__mimicker__/report")

    report = client.get("/__mimicker__/report").json()
    unmatched_paths = [r["path"] for r in report["unmatched_requests"]]
    assert "/__mimicker__/health" not in unmatched_paths
    assert "/__mimicker__/report" not in unmatched_paths
