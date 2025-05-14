import re
from re import Pattern

from mimicker.exceptions import TemplateError


def parse_endpoint_pattern(template: str) -> Pattern:
    """
    Parse an endpoint pattern into a regular expression for URL matching.
    
    This function creates a regex pattern that can match URLs with both static and
    parameterized path segments, as well as query parameters. Path parameters are
    specified using curly braces (e.g., '/{user_id}/profile'). Query parameters
    can be either static or parameterized.
    
    Examples:
        "/users/{id}"                  # Matches: "/users/123"
        "/api/{version}/items"         # Matches: "/api/v1/items"
        "/search?q={term}"             # Matches: "/search?q=python"
        "/filter?min={min}&max={max}"  # Matches: "/filter?min=10&max=100"
    
    Args:
        template: A URL template with optional path and query parameters.
                  Path parameters are specified as {name}.
                  Query parameters can be static or parameterized as key={name}.
    
    Returns:
        A compiled regex Pattern that matches URLs according to the template.
    
    Raises:
        TemplateError: If parameter names are repeated.
        TemplateError: If query parameters do not match the expected URL format.
    """
    try:

        if '?' in template:
            return _parse_with_query(template)

        else:
            return _parse_without_query(template)

    except re.error as e:
        raise TemplateError(f"invalid template: {template!r}") from e


def _parse_without_query(template: str) -> Pattern:
    """
    Parse an endpoint pattern without explicit query parameters.
    
    Creates a regex pattern that matches the path exactly and optionally
    matches any query string (without parsing its contents).
    
    Args:
        template: URL template without a '?' character
        
    Returns:
        Compiled regex Pattern for matching URLs
    """
    path_regex = _build_path_regex(template)
    # Allow any query string (or none) after the path
    full = rf'^{path_regex}(?:\?.*)?$'
    return re.compile(full)


def _parse_with_query(template: str) -> Pattern:
    """
    Parse an endpoint pattern with explicit query parameters.
    
    Creates a regex pattern that matches both the path and specific query parameters.
    Query parameters can be static values or parameterized with {name} syntax.
    
    Args:
        template: URL template containing a '?' followed by query parameters
        
    Returns:
        Compiled regex Pattern for matching URLs with specific query parameters
        
    Raises:
        TemplateError: If a query parameter doesn't contain an equals sign
    """
    path_t, query_t = template.split('?', 1)
    path_regex = _build_path_regex(path_t)

    qpats = []
    for qp in query_t.split('&'):
        if '=' not in qp:
            raise TemplateError(f"invalid query segment (no '=' found): {qp!r}")

        key, val_t = qp.split('=', 1)

        # Handle parameterized query values like key={param}
        if val_t.startswith('{') and val_t.endswith('}'):
            name = val_t[1:-1]
            qpats.append(fr'{re.escape(key)}=(?P<{name}>[^&]+)')  # Named capture group

        else:
            # Handle static query values which are not parameterized
            qpats.append(fr'{re.escape(key)}={re.escape(val_t)}')

    # Construct final regex that matches both path and query parts
    full = rf'^{path_regex}\?{"&".join(qpats)}$'
    return re.compile(full)


def _build_path_regex(path_t: str) -> str:
    """
    Build a regex pattern for matching the path portion of a URL.
    
    Converts a path template with parameterized segments into a regex string.
    Each path segment is either matched literally or converted to a named capture
    group if it's a parameter.
    
    Args:
        path_t: Path template, possibly containing parameters like {name}
        
    Returns:
        A regex string for matching the path (not compiled)
    """
    parts = path_t.strip('/').split('/')
    regex_parts = []
    for part in parts:
        # Check if the part is a parameter (e.g., {id})
        m = re.fullmatch(r'\{(\w+)}', part)
        if m:
            name = m.group(1)  # Extract parameter name from inside braces
            regex_parts.append(
                f'(?P<{name}>[^/?]+)')  # Create named capture group to capture parameter names
        else:
            # Escape special regex characters in literal path segments
            regex_parts.append(re.escape(part))

    # Preserve leading slash and handle empty path case
    return '/' + '/'.join(regex_parts) if parts and parts[0] else '/'
