from hamcrest import assert_that, is_, has_entry, equal_to

from mockingbird.mockingbird import get
from tests.support.client import Client


def test_get_404(mockingbird_server):
    mockingbird_server.routes(
        get("/hello")
    )
    resp = Client().get('/not-found')
    assert_that(resp.status_code, is_(404))


def test_get_default_200_status_code(mockingbird_server):
    mockingbird_server.routes(
        get("/hello")
    )
    resp = Client().get('/hello')
    assert_that(resp.status_code, is_(200))


def test_get_picked_status_code(mockingbird_server):
    mockingbird_server.routes(
        get("/hello").
        status(201)
    )
    resp = Client().get('/hello')
    assert_that(resp.status_code, is_(201))


def test_get_body_as_text(mockingbird_server):
    mockingbird_server.routes(
        get('/hello').
        body("hello world")
    )
    resp = Client().get('/hello')
    assert_that(resp.text, is_("hello world"))


def test_get_body_as_json(mockingbird_server):
    body = {"message": "Hello, World!"}
    mockingbird_server.routes(
        get("/hello").
        body(body).
        status(200)
    )
    resp = Client().get('/hello')
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_get_path_param(mockingbird_server):
    mockingbird_server.routes(
        get("/hello/{greet}").
        body({"message": "Hello, {greet}!"}).
        status(200)
    )
    resp = Client().get('/hello/world')
    assert_that(resp.json(), equal_to({"message": "Hello, world!"}))


def test_get_empty_response(mockingbird_server):
    mockingbird_server.routes(
        get("/empty").
        body(None).
        status(204)
    )
    resp = Client().get('/empty')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_get_headers(mockingbird_server):
    mockingbird_server.routes(
        get("/hello").
        body("hi there").
        headers([("Content-Type", "text/plain")])
    )
    resp = Client().get('/hello', {"Content-Type": "application/json"})
    assert_that(resp.status_code, is_(404))
