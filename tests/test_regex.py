from re import Pattern
from hamcrest import assert_that, equal_to, none, not_none, raises
from mimicker.exceptions import TemplateError
from mimicker.regex import parse_endpoint_pattern


def test_parse_endpoint_pattern_static_path_matches_static_path():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    match = pattern.match("/hello/mimicker")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({}))


def test_parse_endpoint_pattern_static_path_and_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    match = pattern.match("/hello/mimicker/mismatch")
    assert_that(match, none())


def test_parse_endpoint_pattern_with_explicit_query_param_matches_query_param():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker?greeting={name}")
    match = pattern.match("/hello/mimicker?greeting=world")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"name": "world"}))


def test_parse_endpoint_pattern_with_explicit_query_param_and_mismatched_query_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker?mismatched={name}")
    match = pattern.match("/hello/mimicker?greeting=world")
    assert_that(match, none())


def test_parse_endpoint_pattern_without_explicit_query_param_matches_all_query_params():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    match = pattern.match("/hello/mimicker?greeting=world&age=20&city=NewYork")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({}))


def test_parse_endpoint_pattern_path_param_matches_path_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    match = pattern.match("/hello/mimicker")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"greeting": "hello"}))


def test_parse_endpoint_pattern_with_multiple_path_params_matches():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/{name}")
    match = pattern.match("/hello/mimicker")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"greeting": "hello", "name": "mimicker"}))


def test_parse_endpoint_pattern_with_terminal_path_param_doesnt_include_query_params_in_value():
    pattern: Pattern = parse_endpoint_pattern("/hello/{name}")
    match = pattern.match("/hello/mimicker?ignored=param")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"name": "mimicker"}))


def test_parse_endpoint_pattern_path_param_and_path_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    match = pattern.match("/hello/mimicker/mismatch")
    assert_that(match, none())


def test_parse_endpoint_pattern_path_param_and_implicit_query_param_matches_path_param_and_implicit_query_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    match = pattern.match("/hello/mimicker?greeting=world")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"greeting": "hello"}))


def test_parse_endpoint_pattern_path_param_and_query_param_matches_path_param_and_query_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker?age={age}")
    match = pattern.match("/hello/mimicker?age=20")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"greeting": "hello", "age": "20"}))


def test_parse_endpoint_pattern_path_param_and_query_param_and_path_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker?age={age}")
    match = pattern.match("/hello/mimicker/mismatch?greeting=world&age=20&city=NewYork")
    assert_that(match, none())


def test_parse_endpoint_pattern_with_multiple_path_params_and_query_params_matches():
    pattern: Pattern = parse_endpoint_pattern(
        "/some/path/{greeting}/ignored/path/{name}/ignored/2?age={age}&city={city}&ignored=param")
    match = pattern.match(
        "/some/path/hello/ignored/path/mimicker/ignored/2?age=20&city=NewYork&ignored=param")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to(
        {"greeting": "hello", "name": "mimicker", "age": "20", "city": "NewYork"}))


def test_parse_endpoint_pattern_with_repeated_query_param_names_throws_error():
    assert_that(
        lambda: parse_endpoint_pattern(
            "/hello/mimicker?age={age}&city={city}&age={age}"),
        raises(TemplateError)
    )


def test_parse_endpoint_pattern_with_repeated_query_params_distinctly_named_matches():
    pattern: Pattern = parse_endpoint_pattern(
        "/hello/mimicker?greeting={name1}&greeting={name2}")
    match = pattern.match("/hello/mimicker?greeting=world1&greeting=world2")
    assert_that(match, not_none())
    assert_that(match.groupdict(), equal_to({"name1": "world1", "name2": "world2"}))


def test_parse_endpoint_pattern_with_repeated_param_names_throws_error():
    assert_that(
        lambda: parse_endpoint_pattern("/{greeting}/mimicker?greeting={greeting}"),
        raises(TemplateError)
    )


def test_parse_endpoint_pattern_with_repeated_params_distinctly_named_matches():
    pattern: Pattern = parse_endpoint_pattern(
        "/{greeting1}/mimicker?greeting={greeting2}")
    match = pattern.match("/hello/mimicker?greeting=world1")
    assert_that(match, not_none())
    assert_that(match.groupdict(),
                equal_to({"greeting1": "hello", "greeting2": "world1"}))


def test_parse_endpoint_pattern_with_invalid_query_param_throws_error():
    assert_that(
        lambda: parse_endpoint_pattern(
            "/hello/mimicker?age={age1}&city={city}&age{age2}"),
        raises(TemplateError)
    )
