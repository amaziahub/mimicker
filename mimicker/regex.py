import re
from re import Pattern

def parse_endpoint_pattern(template: str) -> Pattern:
    """
    Parse a template into a regex pattern that can extract path and query parameters
    with `match.groupdict()`.

    Args:
        template: A template string like "/{user}/photos" or "/{user}/photos?{key1}={p1}&{key2}={p2}"

    Returns:
        A regex pattern that matches the template.
    """
    if '?' in template:
        return _parse_with_query(template)
    else:
        return _parse_without_query(template)


def _parse_without_query(template: str) -> Pattern:
    """
    No explicit query in the template, match the path exactly,
    then optionally allow ANY query string (or none).
    """
    path_t = template
    path_regex = _build_path_regex(path_t)
    full = rf'^{path_regex}(?:\?.*)?$'
    return re.compile(full)


def _parse_with_query(template: str) -> Pattern:
    """
    Template has form "PATH?key1={p1}&key2={p2}...".  
    We require exactly those keys in that order, capturing each.
    """
    path_t, query_t = template.split('?', 1)
    path_regex = _build_path_regex(path_t)
    qpats = []
    for qp in query_t.split('&'):
        km = re.fullmatch(r'([^=]+)=\{(\w+)\}', qp)
        if not km:
            raise ValueError(f"Invalid query segment: {qp!r}")
        key, name = km.group(1), km.group(2)
        qpats.append(fr'{re.escape(key)}=(?P<{name}>[^&]+)')

    full = rf'^{path_regex}\?{"&".join(qpats)}$'
    return re.compile(full)


def _build_path_regex(path_t: str) -> str:
    """
    Convert a path template like "/{user}/photos" into a regex fragment,
    e.g. "/(?P<user>[^/]+)/photos".
    """
    parts = path_t.strip('/').split('/')
    regex_parts = []
    for part in parts:
        m = re.fullmatch(r'\{(\w+)\}', part)
        if m:
            name = m.group(1)
            regex_parts.append(f'(?P<{name}>[^/]+)')
        else:
            regex_parts.append(re.escape(part))
            
    # Always start with a slash (even for the empty path, yields "/")
    return '/' + '/'.join(regex_parts) if parts and parts[0] else '/'