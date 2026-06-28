# Quickstart

Get a mock server running in under 30 seconds.

---

## 1 — Install

```bash
pip install mimicker
```

---

## 2 — Start a server

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get

    mimicker(8080).routes(
        get("/hello").status(200).body({"message": "Hello, World!"})
    )
    ```

    Run your script — the server starts in a background thread and stays alive until the process exits.

=== "YAML + CLI"

    Create `stubs.yaml`:

    ```yaml
    routes:
      - method: GET
        path: /hello
        status: 200
        body:
          message: Hello, World!
    ```

    Start the server:

    ```bash
    mimicker serve --config stubs.yaml
    ```

=== "Inline (no file)"

    ```bash
    mimicker serve --stub 'GET /hello -> 200 {"message": "Hello, World!"}'
    ```

---

## 3 — Make a request

```bash
curl http://localhost:8080/hello
# {"message": "Hello, World!"}
```

---

## 4 — Use in a test

```python
import pytest
import requests
from mimicker.mimicker import mimicker, get, post


@pytest.fixture(scope="session")
def mock_server():
    server = mimicker(0)   # port 0 = random free port
    server.routes(
        get("/users/1").status(200).body({"id": 1, "name": "Alice"}),
        post("/users").status(201).body({"created": True}),
    )
    yield server
    server.shutdown()


def test_get_user(mock_server):
    url = f"http://localhost:{mock_server.get_port()}/users/1"
    resp = requests.get(url)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alice"


def test_create_user(mock_server):
    url = f"http://localhost:{mock_server.get_port()}/users"
    resp = requests.post(url, json={"name": "Bob"})
    assert resp.status_code == 201
```

!!! tip "Use port 0 in tests"
    Passing `0` to `mimicker()` lets the OS assign a free port automatically — avoids flaky port-conflict failures when tests run in parallel.

---

## Next steps

- [**Stubbing Guide**](../guides/stubbing-guide.md) — all stub options, side-by-side
- [**Path & Query Params**](../guides/path-and-query-params.md)
- [**Dynamic Responses**](../guides/dynamic-responses.md)
- [**Docker**](../ci-cd/docker.md) — run without Python
