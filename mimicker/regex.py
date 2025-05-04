import re

def parse_endpoint_pattern(path: str) -> re.Pattern:
    """
    Parses the endpoint pattern spec into a regular expression that can both match
    the endpoint and extract variables at runtime.

    This function supports parameterized path segments and explicit or implicit query parameters.
    Explicit query parameters (e.g., ?key={value}) are parsed similarly to path parameters.
    If no '?' is present, any query string will be matched implicitly.

    Args:
        path (str): The URL path for the route, supporting parameterized paths and query strings.

    Returns:
        re.Pattern: The regex pattern.
    """
    if '?' in path:
        return _parse_endpoint_pattern_matching_explicit_query_params(path)
    else:
        return _parse_endpoint_pattern_matching_all_query_params(path)


def _parse_endpoint_pattern_matching_all_query_params(path: str) -> re.Pattern:
    path_only = path.split('?', 1)[0]
    parameterized_path = _re_sub_param_name(path_only)
    return re.compile(f"^{parameterized_path}(\\?.*)?$")


def _parse_endpoint_pattern_matching_explicit_query_params(path: str) -> re.Pattern:
    substituted_pattern = _re_sub_param_name(path)
    return re.compile(f"^{substituted_pattern}$")


def _re_sub_param_name(path: str) -> str:
    return re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', path)
