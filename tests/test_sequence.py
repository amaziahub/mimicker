import threading

from hamcrest import assert_that, is_, has_entry

from mimicker.mimicker import get, post
from mimicker.sequence import step
from tests.support.client import Client


def test_sequence_returns_steps_in_order(mimicker_server):
    mimicker_server.routes(
        get("/seq/ordered")
        .sequence(
            step().status(200).body({"step": 1}),
            step().status(202).body({"step": 2}),
            step().status(204).body({"step": 3}),
        )
    )
    client = Client()
    assert_that(client.get("/seq/ordered").status_code, is_(200))
    assert_that(client.get("/seq/ordered").status_code, is_(202))
    assert_that(client.get("/seq/ordered").status_code, is_(204))


def test_sequence_repeats_last_step_by_default(mimicker_server):
    mimicker_server.routes(
        get("/seq/repeat-last")
        .sequence(
            step().status(200).body({"msg": "first"}),
            step().status(500).body({"msg": "last"}),
        )
    )
    client = Client()
    client.get("/seq/repeat-last")
    for _ in range(3):
        resp = client.get("/seq/repeat-last")
        assert_that(resp.status_code, is_(500))
        assert_that(resp.json(), has_entry("msg", "last"))


def test_sequence_cycles_when_enabled(mimicker_server):
    mimicker_server.routes(
        get("/seq/cycle")
        .sequence(
            step().status(200).body({"turn": "a"}),
            step().status(200).body({"turn": "b"}),
            cycle=True,
        )
    )
    client = Client()
    assert_that(client.get("/seq/cycle").json(), has_entry("turn", "a"))
    assert_that(client.get("/seq/cycle").json(), has_entry("turn", "b"))
    assert_that(client.get("/seq/cycle").json(), has_entry("turn", "a"))
    assert_that(client.get("/seq/cycle").json(), has_entry("turn", "b"))


def test_sequence_response_body_is_returned(mimicker_server):
    mimicker_server.routes(
        get("/seq/body")
        .sequence(
            step().status(200).body({"data": "hello"}),
            step().status(200).body({"data": "world"}),
        )
    )
    client = Client()
    assert_that(client.get("/seq/body").json(), has_entry("data", "hello"))
    assert_that(client.get("/seq/body").json(), has_entry("data", "world"))


def test_sequence_single_step_always_returns_same_response(mimicker_server):
    mimicker_server.routes(
        get("/seq/single")
        .sequence(
            step().status(418).body({"msg": "teapot"}),
        )
    )
    client = Client()
    for _ in range(3):
        resp = client.get("/seq/single")
        assert_that(resp.status_code, is_(418))


def test_sequence_works_with_post(mimicker_server):
    mimicker_server.routes(
        post("/seq/post")
        .sequence(
            step().status(201).body({"created": True}),
            step().status(409).body({"error": "conflict"}),
        )
    )
    client = Client()
    assert_that(client.post_as_json("/seq/post").status_code, is_(201))
    assert_that(client.post_as_json("/seq/post").status_code, is_(409))


def test_sequence_is_thread_safe():
    # Uses a dedicated server so concurrent requests don't share state with the
    # session-scoped server, which accumulates stubs from every other test and
    # makes id()-based pattern lookups in _stub_keys unreliable under load.
    from mimicker.mimicker import mimicker as _mimicker
    server = _mimicker(0)
    server.routes(
        get("/seq/concurrent")
        .sequence(
            step().status(200).body({"n": 1}),
            step().status(200).body({"n": 2}),
            step().status(200).body({"n": 3}),
            step().status(200).body({"n": 4}),
            step().status(200).body({"n": 5}),
            cycle=True,
        )
    )
    port = server.get_port()
    client = Client(f"http://localhost:{port}")
    results = []
    lock = threading.Lock()

    def fetch():
        resp = client.get("/seq/concurrent")
        with lock:
            results.append(resp.json()["n"])

    threads = [threading.Thread(target=fetch) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    server.shutdown()

    assert_that(len(results), is_(10))
    assert all(n in [1, 2, 3, 4, 5] for n in results)


def test_sequence_step_headers_are_sent(mimicker_server):
    mimicker_server.routes(
        get("/seq/headers")
        .sequence(
            step().status(200).body({"ok": True}).headers([("X-Step", "one")]),
        )
    )
    client = Client()
    resp = client.get("/seq/headers")
    assert resp.status_code == 200
    assert resp.headers.get("X-Step") == "one"


def test_sequence_step_delay_field():
    s = step().status(200).body({}).delay(0.1)
    assert s._delay == 0.1


def test_sequence_step_with_no_body_returns_empty_response(mimicker_server):
    mimicker_server.routes(
        get("/seq/nobody")
        .sequence(step().status(204))
    )
    client = Client()
    resp = client.get("/seq/nobody")
    assert resp.status_code == 204


def test_sequence_does_not_affect_non_sequence_routes(mimicker_server):
    mimicker_server.routes(
        get("/seq/plain")
        .status(200)
        .body({"static": True})
    )
    client = Client()
    for _ in range(3):
        resp = client.get("/seq/plain")
        assert_that(resp.status_code, is_(200))
        assert_that(resp.json(), has_entry("static", True))
