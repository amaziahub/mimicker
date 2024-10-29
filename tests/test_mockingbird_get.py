import requests
from hamcrest import assert_that, is_, has_entry, equal_to

from mockingbird.mockingbird import get


def test_get_default_200_status_code(mockingbird_server):
    mockingbird_server.routes(
        get("/hello").body({"message": "Hello, World!"})
    )
    response = requests.get('http://localhost:8080/hello')
    assert_that(response.status_code, is_(200))


def test_get_default_application_json_header(mockingbird_server):
    mockingbird_server.routes(
        get("/hello").body({"message": "Hello, World!"}).status(200)
    )
    response = requests.get('http://localhost:8080/hello')
    assert_that(response.headers, has_entry("Content-Type", "application/json"))


def test_get_json_response(mockingbird_server):
    mockingbird_server.routes(
        get("/hello").body({"message": "Hello, World!"}).status(200)
    )
    response = requests.get('http://localhost:8080/hello')
    assert_that(response.headers, has_entry("Content-Type", "application/json"))

    assert_that(response.json(), equal_to({"message": "Hello, World!"}))
