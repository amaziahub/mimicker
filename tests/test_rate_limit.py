from time import sleep

from hamcrest import assert_that, is_, has_entry, not_none
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to

from pytest import mark

from mimicker.mimicker import get
from mimicker.rate_limit import RateLimitTracker, RateLimitConfig
from tests.support.client import Client


class TestRateLimitTracker:
    def test_allows_requests_within_limit(self):
        tracker = RateLimitTracker()
        allowed, remaining, _ = tracker.is_allowed("key", 3, 10)
        assert_that(allowed, is_(True))
        assert_that(remaining, is_(2))

    def test_blocks_requests_exceeding_limit(self):
        tracker = RateLimitTracker()
        for _ in range(3):
            tracker.is_allowed("key", 3, 10)
        allowed, remaining, _ = tracker.is_allowed("key", 3, 10)
        assert_that(allowed, is_(False))
        assert_that(remaining, is_(0))

    def test_allows_requests_to_different_keys_independently(self):
        tracker = RateLimitTracker()
        for _ in range(3):
            tracker.is_allowed("key-a", 3, 10)
        allowed, _, _ = tracker.is_allowed("key-b", 3, 10)
        assert_that(allowed, is_(True))

    def test_resets_after_window_expires(self):
        tracker = RateLimitTracker()
        for _ in range(3):
            tracker.is_allowed("key", 3, 0.1)
        allowed, _, _ = tracker.is_allowed("key", 3, 0.1)
        assert_that(allowed, is_(False))
        sleep(0.11)
        allowed, remaining, _ = tracker.is_allowed("key", 3, 0.1)
        assert_that(allowed, is_(True))
        assert_that(remaining, is_(2))

    def test_remaining_decrements_correctly(self):
        tracker = RateLimitTracker()
        _, r1, _ = tracker.is_allowed("key", 5, 10)
        _, r2, _ = tracker.is_allowed("key", 5, 10)
        _, r3, _ = tracker.is_allowed("key", 5, 10)
        assert_that(r1, is_(4))
        assert_that(r2, is_(3))
        assert_that(r3, is_(2))

    def test_reset_clears_all_windows(self):
        tracker = RateLimitTracker()
        for _ in range(3):
            tracker.is_allowed("key", 3, 10)
        tracker.reset()
        allowed, _, _ = tracker.is_allowed("key", 3, 10)
        assert_that(allowed, is_(True))


class TestRouteRateLimit:
    def test_rate_limit_within_limit_returns_normal_response(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .status(200)
            .rate_limit(max_requests=3, window_seconds=10)
        )
        client = Client()
        resp = client.get("/api/data")
        assert_that(resp.status_code, is_(200))
        assert_that(resp.json(), is_({"ok": True}))

    def test_rate_limit_exceeded_returns_429(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .status(200)
            .rate_limit(max_requests=2, window_seconds=10)
        )
        client = Client()
        client.get("/api/data")
        client.get("/api/data")
        resp = client.get("/api/data")
        assert_that(resp.status_code, is_(429))

    def test_rate_limit_default_body(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .rate_limit(max_requests=1, window_seconds=10)
        )
        client = Client()
        client.get("/api/data")
        resp = client.get("/api/data")
        assert_that(resp.json(), is_({"error": "Too Many Requests"}))

    def test_rate_limit_default_headers(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .rate_limit(max_requests=1, window_seconds=10)
        )
        client = Client()
        client.get("/api/data")
        resp = client.get("/api/data")
        assert_that(resp.headers, has_entry("Retry-After", "10"))

    def test_rate_limit_recovers_after_window(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .rate_limit(max_requests=1, window_seconds=0.1)
        )
        client = Client()
        client.get("/api/data")
        client.get("/api/data")
        sleep(0.15)
        resp = client.get("/api/data")
        assert_that(resp.status_code, is_(200))

    def test_rate_limit_with_key_header(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .rate_limit(max_requests=1, window_seconds=10, key_header="X-Api-Key")
        )
        client = Client()
        resp1 = client.get("/api/data", headers={"X-Api-Key": "key-a"})
        resp2 = client.get("/api/data", headers={"X-Api-Key": "key-a"})
        resp3 = client.get("/api/data", headers={"X-Api-Key": "key-b"})
        assert_that(resp1.status_code, is_(200))
        assert_that(resp2.status_code, is_(429))
        assert_that(resp3.status_code, is_(200))

    def test_rate_limit_custom_429_body_and_status(self, mimicker_server):
        mimicker_server.routes(
            get("/api/data")
            .body({"ok": True})
            .rate_limit(
                max_requests=1, window_seconds=10,
                status_code=429,
                body={"custom": "rate_limited"},
                headers=[("X-Custom", "val"), ("Content-Type", "application/json")]
            )
        )
        client = Client()
        client.get("/api/data")
        resp = client.get("/api/data")
        assert_that(resp.status_code, is_(429))
        assert_that(resp.json(), is_({"custom": "rate_limited"}))

    def test_rate_limit_does_not_affect_other_routes(self, mimicker_server):
        mimicker_server.routes(
            get("/limited")
            .body({"from": "limited"})
            .rate_limit(max_requests=1, window_seconds=10),
            get("/unlimited")
            .body({"from": "unlimited"})
        )
        client = Client()
        client.get("/limited")
        # unlimited should still work
        resp = client.get("/unlimited")
        assert_that(resp.status_code, is_(200))
        assert_that(resp.json(), is_({"from": "unlimited"}))
