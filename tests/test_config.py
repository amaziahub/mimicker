import json
import pytest

from mimicker.config import build_routes, load_config, validate_config


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_yaml(tmp_path):
    p = tmp_path / "stubs.yaml"
    p.write_text(
        "port: 9090\n"
        "routes:\n"
        "  - method: GET\n"
        "    path: /hello\n"
        "    status: 200\n"
        "    body:\n"
        "      message: hi\n"
    )
    return str(p)


@pytest.fixture
def simple_json(tmp_path):
    p = tmp_path / "stubs.json"
    p.write_text(json.dumps({
        "port": 9090,
        "routes": [
            {"method": "GET", "path": "/hello", "status": 200, "body": {"message": "hi"}}
        ]
    }))
    return str(p)


@pytest.fixture
def multi_route_yaml(tmp_path):
    p = tmp_path / "multi.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /a\n"
        "    status: 200\n"
        "  - method: POST\n"
        "    path: /b\n"
        "    status: 201\n"
        "    body:\n"
        "      created: true\n"
        "  - method: DELETE\n"
        "    path: /c/{id}\n"
        "    status: 204\n"
    )
    return str(p)


# ── load_config ───────────────────────────────────────────────────────────────

def test_load_yaml(simple_yaml):
    data = load_config(simple_yaml)
    assert data["port"] == 9090
    assert len(data["routes"]) == 1


def test_load_json(simple_json):
    data = load_config(simple_json)
    assert data["port"] == 9090
    assert len(data["routes"]) == 1


def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_config("/tmp/mimicker-does-not-exist-xyz.yaml")


# ── validate_config ───────────────────────────────────────────────────────────

def test_validate_valid_config():
    data = {"routes": [{"method": "GET", "path": "/hello", "status": 200}]}
    assert validate_config(data) == []


def test_validate_missing_path():
    data = {"routes": [{"method": "GET", "status": 200}]}
    errors = validate_config(data)
    assert any("path" in e for e in errors)


def test_validate_invalid_method():
    data = {"routes": [{"method": "FETCH", "path": "/x", "status": 200}]}
    errors = validate_config(data)
    assert any("method" in e for e in errors)


def test_validate_invalid_status():
    data = {"routes": [{"method": "GET", "path": "/x", "status": 9999}]}
    errors = validate_config(data)
    assert any("status" in e for e in errors)


def test_validate_empty_routes_is_valid():
    assert validate_config({"routes": []}) == []


def test_validate_routes_not_list():
    errors = validate_config({"routes": "not-a-list"})
    assert any("list" in e for e in errors)


def test_validate_route_not_a_mapping():
    errors = validate_config({"routes": ["not-a-dict"]})
    assert any("mapping" in e for e in errors)


def test_validate_sequence_not_a_list():
    data = {"routes": [{"method": "GET", "path": "/x", "status": 200, "sequence": "bad"}]}
    errors = validate_config(data)
    assert any("sequence" in e for e in errors)


# ── build_routes ──────────────────────────────────────────────────────────────

def test_build_routes_count(multi_route_yaml):
    data = load_config(multi_route_yaml)
    routes = build_routes(data)
    assert len(routes) == 3


def test_build_routes_method_and_path(simple_yaml):
    data = load_config(simple_yaml)
    routes = build_routes(data)
    cfg = routes[0].build()
    assert cfg["method"] == "GET"
    assert cfg["path"] == "/hello"


def test_build_routes_status_and_body(simple_yaml):
    data = load_config(simple_yaml)
    routes = build_routes(data)
    cfg = routes[0].build()
    assert cfg["status"] == 200
    assert cfg["body"] == {"message": "hi"}


def test_build_routes_delay_ms_converted_to_seconds(tmp_path):
    p = tmp_path / "delay.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /slow\n"
        "    status: 200\n"
        "    delay_ms: 500\n"
    )
    data = load_config(str(p))
    routes = build_routes(data)
    assert routes[0].build()["delay"] == pytest.approx(0.5)


def test_build_routes_headers_dict(tmp_path):
    p = tmp_path / "headers.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /h\n"
        "    status: 200\n"
        "    headers:\n"
        "      X-Custom: value\n"
        "      Content-Type: application/json\n"
    )
    data = load_config(str(p))
    routes = build_routes(data)
    headers = dict(routes[0].build()["headers"])
    assert headers["X-Custom"] == "value"


def test_build_routes_query_params_appended_to_path(tmp_path):
    p = tmp_path / "qp.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /search\n"
        "    query_params:\n"
        "      active: 'true'\n"
        "    status: 200\n"
    )
    data = load_config(str(p))
    routes = build_routes(data)
    cfg = routes[0].build()
    assert "active=true" in cfg["path"]


def test_build_routes_sequence_step_headers_and_delay(tmp_path):
    p = tmp_path / "seq_hdrs.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /x\n"
        "    sequence:\n"
        "      - status: 200\n"
        "        headers:\n"
        "          X-Step: one\n"
        "        delay_ms: 200\n"
    )
    data = load_config(str(p))
    routes = build_routes(data)
    assert routes[0].build()["sequence"] is not None


def test_build_routes_sequence(tmp_path):
    p = tmp_path / "seq.yaml"
    p.write_text(
        "routes:\n"
        "  - method: GET\n"
        "    path: /flaky\n"
        "    sequence:\n"
        "      - status: 200\n"
        "        body:\n"
        "          ok: true\n"
        "      - status: 500\n"
        "        body:\n"
        "          error: down\n"
        "    cycle: true\n"
    )
    data = load_config(str(p))
    routes = build_routes(data)
    cfg = routes[0].build()
    assert cfg["sequence"] is not None


def test_build_routes_produces_same_route_as_dsl(simple_yaml):
    from mimicker.mimicker import get as dsl_get
    data = load_config(simple_yaml)
    yaml_route = build_routes(data)[0].build()
    dsl_route = dsl_get("/hello").status(200).body({"message": "hi"}).build()
    assert yaml_route["method"] == dsl_route["method"]
    assert yaml_route["path"] == dsl_route["path"]
    assert yaml_route["status"] == dsl_route["status"]
    assert yaml_route["body"] == dsl_route["body"]
