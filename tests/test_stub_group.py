from hamcrest import assert_that, none, is_

from mimicker.stub_group import StubGroup


def test_none_given_no_stubs():
    stub_group = StubGroup()
    matched, _ = stub_group.match("GET", "/hello/kuku")
    assert_that(matched, none())


def test_no_match():
    stub_group = StubGroup()
    stub_group.add("GET", "/hi", 200, {"message": "hello"})
    matched, _ = stub_group.match("GET", "/hello/kuku")
    assert_that(matched, none())


def test_match():
    stub_group = StubGroup()
    stub_group.add("GET", "/hi", 200, {"message": "hello"})
    matched, _ = stub_group.match("GET", "/hi")
    assert_that(matched, is_((200, 0, {"message": "hello"}, None, None)))


def test_none_on_partial_match():
    stub_group = StubGroup()
    stub_group.add("POST", "/hi", 200, {"message": "hello"})
    matched, _ = stub_group.match("POST", "/hi/hello")
    assert_that(matched, none())


def test_match_w_path_param():
    stub_group = StubGroup()
    stub_group.add("GET",
                   r"^/hello/(?P<name>\w+)$",
                   200,
                   {"message": "Hello, {name}!"})

    matched, path_param = stub_group.match("GET", "/hello/mimicker")

    assert_that(matched, is_((200, 0, {"message": "Hello, {name}!"}, None, None)))
    assert_that(path_param, is_({"name": "mimicker"}))

def test_match_w_delay():
    stub_group = StubGroup()
    stub_group.add("GET", "/hi", 200, {"message": "hello"}, delay=3)

    matched, _ = stub_group.match("GET", "/hi")

    assert_that(matched, is_((200, 3, {"message": "hello"}, None, None)))


def test_match_stub_with_response_func():
    stub_group = StubGroup()

    def dynamic_response():
        return 202, {"status": "dynamic"}

    stub_group.add("GET", r"^/dynamic$",
                   200, {}, response_func=dynamic_response)
    matched, _ = stub_group.match("GET", "/dynamic")
    assert_that(matched, is_((200, 0, {}, dynamic_response, None)))


def test_match_given_unexpected_header():
    stub_group = StubGroup()
    stub_group.add(
        "GET", "/hi", 200,
        {"message": "hello"}, headers=[("Content-Type", "text/plain")])
    matched, _ = stub_group.match(
        "GET", "/hi",
        request_headers={"Content-Type": "application/json"})
    assert_that(matched, is_((200, 0, {'message': 'hello'}, None,
                              [('Content-Type', 'text/plain')])))


def test_match_given_partial_expected_headers():
    stub_group = StubGroup()
    stub_group.add("GET", "/hi", 200,
                   {"message": "hello"},
                   headers=[
                       ("Content-Type", "application/json"),
                       ("Authorization", "Bearer YOUR_TOKEN"),
                       ("Custom-Header", "CustomValue")
                   ])
    matched, _ = stub_group.match(
        "GET", "/hi",
        request_headers={"Content-Type": "application/json"})
    assert_that(matched, is_((200, 0, {'message': 'hello'},
                              None, [
                                  ('Content-Type', 'application/json'),
                                  ('Authorization', 'Bearer YOUR_TOKEN'),
                                  ('Custom-Header', 'CustomValue')])))
