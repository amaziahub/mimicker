import json
import os
from typing import Any, Dict, List

from mimicker.route import Route
from mimicker.sequence import SequenceStep


_VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}


def load_config(path: str) -> Dict[str, Any]:
    """Load and parse a YAML or JSON stub config file."""
    _, ext = os.path.splitext(path.lower())
    with open(path) as f:
        if ext in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError:
                raise ImportError(
                    "PyYAML is required to load YAML config files. "
                    "Install it with: pip install pyyaml"
                )
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    return data or {}


def validate_config(data: Dict[str, Any]) -> List[str]:
    """Validate config data. Returns a list of human-readable error messages."""
    errors = []
    routes = data.get("routes", [])
    if not isinstance(routes, list):
        errors.append("'routes' must be a list")
        return errors

    for i, route in enumerate(routes):
        prefix = f"routes[{i}]"
        if not isinstance(route, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue
        method = str(route.get("method", "")).upper()
        if method not in _VALID_METHODS:
            errors.append(
                f"{prefix}: invalid method {route.get('method')!r}. "
                f"Must be one of {sorted(_VALID_METHODS)}"
            )
        if not route.get("path"):
            errors.append(f"{prefix}: 'path' is required")
        status = route.get("status", 200)
        if not isinstance(status, int) or not (100 <= status <= 599):
            errors.append(f"{prefix}: 'status' must be an HTTP status code integer")
        if "sequence" in route and not isinstance(route["sequence"], list):
            errors.append(f"{prefix}: 'sequence' must be a list of step objects")

    return errors


def build_routes(data: Dict[str, Any]) -> List[Route]:
    """Convert validated config data into Route objects."""
    routes = []
    for r in data.get("routes", []):
        method = str(r.get("method", "GET")).upper()
        path = r.get("path", "/")

        # Append explicit query_params to the path so the existing regex engine handles them
        if "query_params" in r and isinstance(r["query_params"], dict):
            qp_str = "&".join(f"{k}={v}" for k, v in r["query_params"].items())
            path = f"{path}?{qp_str}"

        route = Route(method, path)

        if "status" in r:
            route.status(int(r["status"]))
        if "body" in r:
            route.body(r["body"])
        if "headers" in r:
            h = r["headers"]
            route.headers(list(h.items()) if isinstance(h, dict) else h)
        if "delay_ms" in r:
            route.delay(float(r["delay_ms"]) / 1000.0)

        if "sequence" in r:
            steps = []
            for step_data in r["sequence"]:
                s = SequenceStep()
                if "status" in step_data:
                    s.status(int(step_data["status"]))
                if "body" in step_data:
                    s.body(step_data["body"])
                if "headers" in step_data:
                    h = step_data["headers"]
                    s.headers(list(h.items()) if isinstance(h, dict) else h)
                if "delay_ms" in step_data:
                    s.delay(float(step_data["delay_ms"]) / 1000.0)
                steps.append(s)
            route.sequence(*steps, cycle=bool(r.get("cycle", False)))

        routes.append(route)
    return routes
