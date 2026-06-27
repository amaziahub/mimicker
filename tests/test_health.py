import pytest
from hamcrest import assert_that, is_, has_entry

from mimicker.mimicker import mimicker, get
from tests.support.client import Client


@pytest.fixture(scope="module")
def health_server():
    server = mimicker(port=0)
    yield server
    server.shutdown()


def test_health_endpoint_returns_200(health_server):
    port = health_server.get_port()
    client = Client(f"http://localhost:{port}")
    resp = client.get("/__mimicker__/health")
    assert_that(resp.status_code, is_(200))


def test_health_endpoint_returns_json_status(health_server):
    port = health_server.get_port()
    client = Client(f"http://localhost:{port}")
    resp = client.get("/__mimicker__/health")
    assert_that(resp.json(), has_entry("status", "up"))


def test_health_endpoint_present_with_no_routes(health_server):
    port = health_server.get_port()
    client = Client(f"http://localhost:{port}")
    resp = client.get("/__mimicker__/health")
    assert_that(resp.status_code, is_(200))


def test_health_endpoint_present_alongside_user_routes(health_server):
    port = health_server.get_port()
    health_server.routes(
        get("/my-route").status(200).body({"ok": True})
    )
    client = Client(f"http://localhost:{port}")
    assert_that(client.get("/my-route").status_code, is_(200))
    assert_that(client.get("/__mimicker__/health").status_code, is_(200))


def test_health_endpoint_does_not_conflict_with_user_routes(health_server):
    port = health_server.get_port()
    client = Client(f"http://localhost:{port}")
    # User-defined route returns 404 for unknown paths
    resp = client.get("/not-a-real-route-xyz")
    assert_that(resp.status_code, is_(404))
    # Health is still up
    assert_that(client.get("/__mimicker__/health").status_code, is_(200))
