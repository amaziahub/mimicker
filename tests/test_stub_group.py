from hamcrest import assert_that, none, is_
from mockingbird.stub_group import StubGroup


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
    assert_that(matched, is_((200, {"message": "hello"}, None)))


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

    matched, path_param = stub_group.match("GET", "/hello/mockingbird")

    assert_that(matched, is_((200, {"message": "Hello, {name}!"}, None)))
    assert_that(path_param, is_({"name": "mockingbird"}))


def test_match_stub_with_response_func():
    stub_group = StubGroup()

    def dynamic_response():
        return 202, {"status": "dynamic"}

    stub_group.add("GET", r"^/dynamic$",
                   200, {}, response_func=dynamic_response)
    matched, _ = stub_group.match("GET", "/dynamic")
    assert_that(matched, is_((200, {}, dynamic_response)))
