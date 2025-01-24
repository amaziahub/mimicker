from time import perf_counter
from requests.exceptions import ReadTimeout

from hamcrest import assert_that, is_, has_entry, equal_to
from hamcrest.library.number.ordering_comparison import greater_than_or_equal_to
from hamcrest.library.number.iscloseto import close_to

from pytest import mark, raises

from mimicker.mimicker import get
from tests.support.client import Client


def test_get_404(mimicker_server):
    mimicker_server.routes(
        get("/hello")
    )
    resp = Client().get('/not-found')
    assert_that(resp.status_code, is_(404))


def test_get_default_200_status_code(mimicker_server):
    mimicker_server.routes(
        get("/hello")
    )
    resp = Client().get('/hello')
    assert_that(resp.status_code, is_(200))


def test_get_picked_status_code(mimicker_server):
    mimicker_server.routes(
        get("/hello").
        status(201)
    )
    resp = Client().get('/hello')
    assert_that(resp.status_code, is_(201))


def test_get_body_as_text(mimicker_server):
    mimicker_server.routes(
        get('/hello').
        body("hello world")
    )
    resp = Client().get('/hello')
    assert_that(resp.text, is_("hello world"))


def test_get_body_as_json(mimicker_server):
    body = {"message": "Hello, World!"}
    mimicker_server.routes(
        get("/hello").
        body(body).
        status(200)
    )
    resp = Client().get('/hello')
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_get_path_param(mimicker_server):
    mimicker_server.routes(
        get("/hello/{greet}").
        body({"message": "Hello, {greet}!"}).
        status(200)
    )
    resp = Client().get('/hello/world')
    assert_that(resp.json(), equal_to({"message": "Hello, world!"}))


def test_get_empty_response(mimicker_server):
    mimicker_server.routes(
        get("/empty").
        body(None).
        status(204)
    )
    resp = Client().get('/empty')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_get_headers(mimicker_server):
    mimicker_server.routes(
        get("/hello").
        body("hi there").
        headers([("Content-Type", "text/plain")])
    )
    resp = Client().get('/hello', {"Content-Type": "application/json"})
    assert_that(resp.status_code, is_(200))

@mark.parametrize(
    "delay_in_seconds",
    [0.1, 0.2, 0.5],
)
def test_get_with_delay(mimicker_server, delay_in_seconds: float):
    mimicker_server.routes(
        get("/wait").
        delay(delay_in_seconds).
        body("finally here")
    )

    start = perf_counter()
    resp = Client().get('/wait')
    duration_seconds = perf_counter() - start

    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_("finally here"))
    assert_that(duration_seconds, is_(greater_than_or_equal_to(delay_in_seconds)))
    assert_that(duration_seconds, is_(close_to(delay_in_seconds, 0.05)))

def test_get_with_timedout_delay(mimicker_server):
    mimicker_server.routes(
        get("/wait").
        delay(0.1).
        body("finally here")
    )

    with raises(ReadTimeout) as error:
        Client().get('/wait', timeout=0.05)

    assert_that(str(error.value), is_("HTTPConnectionPool(host='localhost', port=8080): Read timed out. (read timeout=0.05)"))
