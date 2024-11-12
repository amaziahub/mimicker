from hamcrest import assert_that, is_, has_entry, equal_to

from mockingbird.mockingbird import post
from tests.support.client import Client


def test_post_404(mockingbird_server):
    mockingbird_server.routes(
        post("/submit")
    )
    resp = Client().post_as_json('/not-found')
    assert_that(resp.status_code, is_(404))


def test_post_default_200_status_code(mockingbird_server):
    mockingbird_server.routes(
        post("/submit")
    )
    resp = Client().post_as_json('/submit')
    assert_that(resp.status_code, is_(200))


def test_post_picked_status_code(mockingbird_server):
    mockingbird_server.routes(
        post("/submit").
        status(201)
    )
    resp = Client().post_as_json('/submit')
    assert_that(resp.status_code, is_(201))


def test_post_body_as_text(mockingbird_server):
    mockingbird_server.routes(
        post('/submit').
        body("submission successful")
    )
    resp = Client().post_as_text('/submit', body="submission successful")
    assert_that(resp.text, is_("submission successful"))


def test_post_body_as_json(mockingbird_server):
    body = {"result": "created"}
    mockingbird_server.routes(
        post("/submit").
        body(body).
        status(201)
    )
    resp = Client().post_as_json('/submit', body=body)
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_post_empty_response(mockingbird_server):
    mockingbird_server.routes(
        post("/clear").
        body(None).
        status(204)
    )
    resp = Client().post_as_json('/clear')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_post_body_with_text_content(mockingbird_server):
    body = "This is a plain text submission."
    mockingbird_server.routes(
        post("/submit-text").
        body(body).
        status(200)
    )
    resp = Client().post_as_text('/submit-text', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_(body))


def test_post_body_with_json_content(mockingbird_server):
    body = {"message": "Data submitted"}
    mockingbird_server.routes(
        post("/submit-json").
        body(body).
        status(201)
    )
    resp = Client().post_as_json('/submit-json', body=body)
    assert_that(resp.status_code, is_(201))
    assert_that(resp.json(), equal_to(body))


def test_post_file_upload(mockingbird_server):
    file_content = b"Test file content"
    mockingbird_server.routes(
        post("/upload").
        body("File uploaded successfully").
        status(200)
    )
    with open('/tmp/test_file.txt', 'wb') as f:
        f.write(file_content)

    with open('/tmp/test_file.txt', 'rb') as file:
        resp = Client().post_as_file('/upload', body={'file': file})

    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_("File uploaded successfully"))
