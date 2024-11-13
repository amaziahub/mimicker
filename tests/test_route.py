import re
from mimicker.route import Route
from hamcrest import assert_that, equal_to, has_entry, instance_of


def test_route_initialization():
    route = Route("GET", "/hello")
    assert_that(route.method, equal_to("GET"))
    assert_that(route.path, equal_to("/hello"))
    assert_that(route._status, equal_to(200))
    assert_that(route._body, equal_to({}))


def test_route_body():
    route = Route("GET", "/hello").body({"message": "Hello, World!"})
    assert_that(route._body, has_entry("message", "Hello, World!"))


def test_route_status():
    route = Route("GET", "/hello").status(404)
    assert_that(route._status, equal_to(404))


def test_route_with_path_parameter():
    route = Route("GET", "/hello/{greet}")
    compiled_path = route._compiled_path
    match = compiled_path.match("/hello/world")
    assert_that(match.group("greet"), equal_to("world"))


def test_route_build():
    route = (Route("GET", "/hello/{greet}")
             .body({"message": "Hello, {greet}!"})
             .status(201))
    route_config = route.build()

    assert_that(route_config["method"], equal_to("GET"))
    assert_that(route_config["path"], equal_to("/hello/{greet}"))
    assert_that(route_config["status"], equal_to(201))
    assert_that(route_config["body"], equal_to({"message": "Hello, {greet}!"}))
    assert_that(route_config["compiled_path"], instance_of(re.Pattern))


def test_route_response_func():
    def mock_response_func():
        return 202, {"message": "Generated dynamically"}

    route = Route("GET", "/dynamic").response_func(mock_response_func)
    route_config = route.build()

    assert_that(route_config["response_func"], equal_to(mock_response_func))

    status_code, response = route_config["response_func"]()
    assert_that(status_code, equal_to(202))
    assert_that(response, equal_to({"message": "Generated dynamically"}))
