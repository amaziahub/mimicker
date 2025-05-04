import re
from re import Pattern

def parse_endpoint_pattern(template: str) -> Pattern:
    if '?' in template:
        return _parse_with_query(template)
    
    else:
        return _parse_without_query(template)


def _build_path_regex(path_t: str) -> str:
    parts = path_t.strip('/').split('/')
    regex_parts = []
    for part in parts:
        m = re.fullmatch(r'\{(\w+)\}', part)
        if m:
            name = m.group(1)
            regex_parts.append(f'(?P<{name}>[^/]+)')
        else:
            regex_parts.append(re.escape(part))
    return '/' + '/'.join(regex_parts) if parts and parts[0] else '/'


def _parse_without_query(template: str) -> Pattern:
    path_regex = _build_path_regex(template)
    full = rf'^{path_regex}(?:\?.*)?$'
    return re.compile(full)


def _parse_with_query(template: str) -> Pattern:
    path_t, query_t = template.split('?', 1)
    path_regex = _build_path_regex(path_t)
    qpats = []
    for qp in query_t.split('&'):
        if '=' not in qp:
            raise ValueError(f"Invalid query segment (no '=' found): {qp!r}")
        key, val_t = qp.split('=', 1)

        if val_t.startswith('{') and val_t.endswith('}'):
            name = val_t[1:-1]
            qpats.append(fr'{re.escape(key)}=(?P<{name}>[^&]+)')

        else:
            qpats.append(fr'{re.escape(key)}={re.escape(val_t)}')

    full = rf'^{path_regex}\?{"&".join(qpats)}$'
    return re.compile(full)
