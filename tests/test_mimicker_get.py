from concurrent.futures import ThreadPoolExecutor
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


def test_get_query_param(mimicker_server):
    def handle_request(**kwargs):
        return 200, {"message": f"Hello, {kwargs['query']['greet'][0]}!"}

    mimicker_server.routes(
        get("/hello").
        response_func(handle_request)
    )
    resp = Client().get('/hello?greet=world')
    assert_that(resp.json(), equal_to({"message": "Hello, world!"}))


def test_get_with_query_param_spec_matches(mimicker_server):
    mimicker_server.routes(
        get("/hello?greeting={greet}").
        body({"message": "Hello, {greet}!"}).
        status(200)
    )
    resp = Client().get('/hello?greeting=world')
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

    assert_that(str(error.value),
                is_("HTTPConnectionPool(host='localhost', port=8080): Read timed out. (read timeout=0.05)"))


def _call_route_and_measure_duration(client: Client, route: str) -> float:
    """
    Performs the call and return its duration in seconds.
    """
    start = perf_counter()
    client.get(route)
    return perf_counter() - start


def test_get_delays_should_affect_only_their_respective_call(mimicker_server):
    """
    Ensures that the delay of a stub group affects only the given route.
    """

    slow_delay = 0.1
    medium_delay = 0.01
    mimicker_server.routes(
        get("/slow").delay(slow_delay).body("slowly here"),
        get("/medium").delay(medium_delay).body("here"),
        get("/rapid").body("rapidly here"),
    )

    client = Client()
    with ThreadPoolExecutor(max_workers=2) as executor:
        slow_call_future = executor.submit(_call_route_and_measure_duration, client, "/slow")
        medium_call_future = executor.submit(_call_route_and_measure_duration, client, "/medium")
        rapid_call_future = executor.submit(_call_route_and_measure_duration, client, "/rapid")
        slow_call_duration = slow_call_future.result()
        medium_call_duration = medium_call_future.result()
        rapid_call_duration = rapid_call_future.result()

    assert_that(slow_call_duration, is_(greater_than_or_equal_to(slow_delay)))
    assert_that(slow_call_duration, is_(close_to(slow_delay, 0.05)))

    assert_that(medium_call_duration, is_(greater_than_or_equal_to(medium_delay)))
    assert_that(medium_call_duration, is_(close_to(medium_delay, 0.05)))

    assert_that(rapid_call_duration, is_(greater_than_or_equal_to(0)))
    assert_that(rapid_call_duration, is_(close_to(0, 0.05)))
