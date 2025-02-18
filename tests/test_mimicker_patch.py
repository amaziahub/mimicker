from hamcrest import assert_that, is_, has_entry, equal_to

from mimicker.mimicker import patch
from tests.support.client import Client


def test_patch_404(mimicker_server):
    mimicker_server.routes(
        patch("/modify")
    )
    resp = Client().patch('/not-found')
    assert_that(resp.status_code, is_(404))


def test_patch_default_200_status_code(mimicker_server):
    mimicker_server.routes(
        patch("/modify")
    )
    resp = Client().patch('/modify')
    assert_that(resp.status_code, is_(200))


def test_patch_picked_status_code(mimicker_server):
    mimicker_server.routes(
        patch("/modify").
        status(202)
    )
    resp = Client().patch('/modify')
    assert_that(resp.status_code, is_(202))


def test_patch_body_as_text(mimicker_server):
    mimicker_server.routes(
        patch('/modify').
        body("modification successful")
    )
    resp = Client().patch_as_text('/modify', body="modification successful")
    assert_that(resp.text, is_("modification successful"))


def test_patch_body_as_json(mimicker_server):
    body = {"result": "modified"}
    mimicker_server.routes(
        patch("/modify").
        body(body).
        status(200)
    )
    resp = Client().patch_as_json('/modify', body=body)
    assert_that(resp.headers, has_entry("Content-Type", "application/json"))
    assert_that(resp.json(), equal_to(body))


def test_patch_empty_response(mimicker_server):
    mimicker_server.routes(
        patch("/clear").
        body(None).
        status(204)
    )
    resp = Client().patch('/clear')
    assert_that(resp.status_code, is_(204))
    assert_that(resp.text, is_(""))


def test_patch_text_content(mimicker_server):
    body = "This is a modification with plain text."
    mimicker_server.routes(
        patch("/modify-text").
        body(body).
        status(200)
    )
    resp = Client().patch_as_text('/modify-text', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.text, is_(body))


def test_patch_json_content(mimicker_server):
    body = {"message": "Modified successfully"}
    mimicker_server.routes(
        patch("/modify-json").
        body(body).
        status(200)
    )
    resp = Client().patch_as_json('/modify-json', body=body)
    assert_that(resp.status_code, is_(200))
    assert_that(resp.json(), equal_to(body))
