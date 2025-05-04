from re import Pattern
from hamcrest import assert_that, is_, none, not_none
from mimicker.regex import parse_endpoint_pattern

def test_parse_endpoint_pattern_static_path_matches_static_path():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    assert_that(pattern.match("/hello/mimicker"), not_none())


def test_parse_endpoint_pattern_static_path_and_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    assert_that(pattern.match("/hello/mimicker/mismatch"), none())


def test_parse_endpoint_pattern_with_explicit_query_param_matches_query_param():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker?greeting={name}")
    assert_that(pattern.match("/hello/mimicker?greeting=world"), not_none())


def test_parse_endpoint_pattern_with_explicit_query_param_and_mismatched_query_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker?mismatched={name}")
    assert_that(pattern.match("/hello/mimicker?greeting=world"), none())


def test_parse_endpoint_pattern_without_explicit_query_param_matches_all_query_params():
    pattern: Pattern = parse_endpoint_pattern("/hello/mimicker")
    assert_that(pattern.match("/hello/mimicker?greeting=world&age=20&city=NewYork"), not_none())


def test_parse_endpoint_pattern_path_param_matches_path_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    assert_that(pattern.match("/hello/mimicker?greeting=world&age=20&city=NewYork"), not_none())


def test_parse_endpoint_pattern_path_param_and_path_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    assert_that(pattern.match("/hello/mimicker/mismatch"), none())


def test_parse_endpoint_pattern_path_param_and_implicit_query_param_matches_path_param_and_implicit_query_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker")
    assert_that(pattern.match("/hello/mimicker?greeting=world"), not_none())


def test_parse_endpoint_pattern_path_param_and_query_param_matches_path_param_and_query_param():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker?age={age}")
    assert_that(pattern.match("/hello/mimicker?age=20"), not_none())


def test_parse_endpoint_pattern_path_param_and_query_param_and_path_mismatched_path_does_not_match():
    pattern: Pattern = parse_endpoint_pattern("/{greeting}/mimicker?age={age}")
    assert_that(pattern.match("/hello/mimicker/mismatch?greeting=world&age=20&city=NewYork"), none())
    