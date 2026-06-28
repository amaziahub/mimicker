"""
Backward-compatibility contract for mimicker's public API.

Every pattern here reflects usage that existed before the CI/CD DevX changes
(Sequence feature, tracking, health/report endpoints, Docker, CLI).
Nothing in this file should ever break without a deliberate major-version bump.
"""
import pytest
from mimicker.mimicker import get, post, put, delete, patch, mimicker, MimickerServer, Route
from tests.support.client import Client


# ── Public API surface ────────────────────────────────────────────────────────

def test_factory_functions_return_route():
    assert isinstance(get("/x"), Route)
    assert isinstance(post("/x"), Route)
    assert isinstance(put("/x"), Route)
    assert isinstance(delete("/x"), Route)
    assert isinstance(patch("/x"), Route)


def test_mimicker_returns_server_instance():
    server = mimicker(0)
    assert isinstance(server, MimickerServer)
    server.shutdown()


def test_server_chainable_routes():
    server = mimicker(0)
    result = server.routes(get("/a").status(200))
    assert result is server
    server.shutdown()


def test_get_port_returns_int():
    server = mimicker(0)
    assert isinstance(server.get_port(), int)
    server.shutdown()


# ── Route builder chain ───────────────────────────────────────────────────────

def test_status_and_body(mimicker_server):
    mimicker_server.routes(get("/bc/status-body").status(201).body({"ok": True}))
    resp = Client().get("/bc/status-body")
    assert resp.status_code == 201
    assert resp.json() == {"ok": True}


def test_string_body(mimicker_server):
    mimicker_server.routes(get("/bc/str-body").status(200).body("hello"))
    assert Client().get("/bc/str-body").text == "hello"


def test_custom_headers(mimicker_server):
    mimicker_server.routes(
        get("/bc/headers")
        .status(200)
        .body({"x": 1})
        .headers([("X-Custom", "abc"), ("X-Other", "123")])
    )
    resp = Client().get("/bc/headers")
    assert resp.headers["X-Custom"] == "abc"
    assert resp.headers["X-Other"] == "123"


def test_delay(mimicker_server):
    import time
    mimicker_server.routes(get("/bc/delay").status(200).delay(0.1).body({"slow": True}))
    start = time.monotonic()
    Client().get("/bc/delay")
    assert time.monotonic() - start >= 0.1


def test_url_path_params(mimicker_server):
    mimicker_server.routes(get("/bc/users/{id}").status(200).body({"id": "{id}"}))
    resp = Client().get("/bc/users/42")
    assert resp.json()["id"] == "42"


def test_404_for_unregistered_path(mimicker_server):
    assert Client().get("/bc/no-such-route-xyz").status_code == 404


def test_empty_body(mimicker_server):
    mimicker_server.routes(get("/bc/empty").status(204).body(None))
    resp = Client().get("/bc/empty")
    assert resp.status_code == 204
    assert resp.text == ""


# ── response_func ─────────────────────────────────────────────────────────────

def test_response_func_basic(mimicker_server):
    def my_func(**kwargs):
        return 202, {"computed": True}

    mimicker_server.routes(get("/bc/func").response_func(my_func))
    resp = Client().get("/bc/func")
    assert resp.status_code == 202
    assert resp.json()["computed"] is True


def test_response_func_uses_path_params(mimicker_server):
    def echo_id(**kwargs):
        return 200, {"echo": kwargs["params"].get("id")}

    mimicker_server.routes(get("/bc/echo/{id}").response_func(echo_id))
    assert Client().get("/bc/echo/99").json()["echo"] == "99"


def test_response_func_returning_none_body_gives_empty_response(mimicker_server):
    # Locking down the correct behavior: None body writes nothing (not the string "None").
    def func_none(**kwargs):
        return 200, None

    mimicker_server.routes(get("/bc/func-none").response_func(func_none))
    resp = Client().get("/bc/func-none")
    assert resp.status_code == 200
    assert resp.text == ""


# ── HTTP methods ──────────────────────────────────────────────────────────────

def test_post_route(mimicker_server):
    mimicker_server.routes(post("/bc/items").status(201).body({"created": True}))
    assert Client().post_as_json("/bc/items").status_code == 201


def test_put_route(mimicker_server):
    mimicker_server.routes(put("/bc/items/1").status(200).body({"updated": True}))
    assert Client().put("/bc/items/1").status_code == 200


def test_delete_route(mimicker_server):
    mimicker_server.routes(delete("/bc/items/1").status(204))
    assert Client().delete("/bc/items/1").status_code == 204


def test_patch_route(mimicker_server):
    mimicker_server.routes(patch("/bc/items/1").status(200).body({"patched": True}))
    assert Client().patch("/bc/items/1").status_code == 200


# ── Admin endpoint precedence ─────────────────────────────────────────────────

def test_user_stub_at_health_path_takes_precedence():
    """If a user registers a stub at /__mimicker__/health, it wins over the admin handler."""
    server = mimicker(0)
    server.routes(get("/__mimicker__/health").status(503).body({"status": "custom"}))
    client = Client(f"http://localhost:{server.get_port()}")
    resp = client.get("/__mimicker__/health")
    assert resp.status_code == 503
    assert resp.json()["status"] == "custom"
    server.shutdown()


def test_admin_health_endpoint_is_fallback():
    """Without a user stub, /__mimicker__/health returns the built-in admin response."""
    server = mimicker(0)
    client = Client(f"http://localhost:{server.get_port()}")
    resp = client.get("/__mimicker__/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "up"
    server.shutdown()


def test_health_pings_do_not_appear_in_unmatched_report():
    """Admin path hits must not pollute the unmatched-request tracking."""
    server = mimicker(0)
    client = Client(f"http://localhost:{server.get_port()}")
    client.get("/__mimicker__/health")
    client.get("/__mimicker__/health")
    report = client.get("/__mimicker__/report").json()
    unmatched_paths = [r["path"] for r in report["unmatched_requests"]]
    assert "/__mimicker__/health" not in unmatched_paths
    server.shutdown()
