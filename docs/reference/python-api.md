# Python API

Full method reference for the Mimicker Python DSL.

---

## `mimicker(port)`

Start a Mimicker server on the given port. Returns a `MimickerServer` instance.

```python
from mimicker.mimicker import mimicker

server = mimicker(8080)
server = mimicker(0)   # OS assigns a free port
```

### Methods

#### `.routes(*routes)`

Register one or more stubs.

```python
from mimicker.mimicker import mimicker, get, post

server = mimicker(8080).routes(
    get("/users").status(200).body({"users": []}),
    post("/users").status(201).body({"created": True}),
)
```

#### `.load_config(path)`

Load stubs from a YAML or JSON file.

```python
server = mimicker(8080).load_config("test/stubs.yaml")
```

#### `.get_port()`

Return the actual port in use (useful when `port=0` was passed).

```python
server = mimicker(0)
print(server.get_port())   # e.g. 54321
```

#### `.shutdown()`

Stop the server and release the port.

```python
server.shutdown()
```

Use in `teardown` or pytest fixtures to avoid port leaks between tests.

---

## HTTP method helpers

Import from `mimicker.mimicker`:

```python
from mimicker.mimicker import get, post, put, delete, patch
```

Each returns a `Route` builder:

```python
get("/path")
post("/path")
put("/path")
delete("/path")
patch("/path")
```

---

## `Route` builder

### `.status(code)`

Set the HTTP response status code.

```python
get("/ping").status(200)
delete("/items/1").status(204)
get("/missing").status(404)
```

### `.body(data)`

Set the response body. Accepts a `dict`, `list`, `str`, `int`, `float`, or `None`.

```python
get("/users").status(200).body({"users": []})
get("/raw").status(200).body("plain text")
get("/number").status(200).body(42)
delete("/items/1").status(204)   # no body needed
```

`None` produces an empty response body (not the string `"None"`).

### `.headers(header_list)`

Set response headers. Pass a list of `(name, value)` tuples.

```python
get("/secure")
.status(200)
.headers([
    ("Content-Type", "application/json"),
    ("X-Custom", "value"),
])
.body({"ok": True})
```

### `.delay(seconds)`

Add an artificial delay before responding.

```python
get("/slow").delay(0.5).status(200).body({"result": "ok"})
```

### `.sequence(*steps, cycle=False)`

Return a different response on each successive call.

```python
from mimicker.mimicker import get
from mimicker.sequence import step

get("/flaky").sequence(
    step().status(200).body({"ok": True}),
    step().status(503).body({"error": "down"}),
    step().status(200).body({"ok": True}),
)
```

Pass `cycle=True` to loop back to the first step after the last:

```python
get("/alternating").sequence(
    step().status(200).body({"ok": True}),
    step().status(500).body({"error": "boom"}),
    cycle=True,
)
```

### `.rate_limit(...)`

Simulate rate limiting.

```python
get("/api/data")
.rate_limit(
    max_requests=5,
    window_seconds=60,
)
```

Full signature:

```python
.rate_limit(
    max_requests: int,
    window_seconds: float,
    status_code: int = 429,
    body: dict | str | None = None,
    headers: list[tuple[str, str]] | None = None,
    key_header: str | None = None,   # per-client rate limiting
)
```

### `.response_func(func)`

Compute the response dynamically from request data.

```python
def my_func(**kwargs):
    payload = kwargs.get("payload") or {}
    name = payload.get("name", "Guest")
    return 200, {"message": f"Hello, {name}!"}

post("/greet").response_func(my_func)
```

`func` must accept `**kwargs`. Available keys:

| Key | Type | Description |
|---|---|---|
| `payload` | `dict \| None` | Parsed JSON request body |
| `headers` | `dict[str, str]` | Lowercased request headers |
| `params` | `dict[str, str]` | Path parameter values |
| `query_params` | `dict[str, list[str]]` | Query string parameters |

Return value: `(int, dict | str | None)` — status code and body.

---

## `step()` — sequence steps

Import from `mimicker.sequence`:

```python
from mimicker.sequence import step
```

`step()` returns a `SequenceStep` builder with the same `.status()`, `.body()`, `.headers()`, and `.delay()` methods as `Route`.

```python
step().status(200).body({"ok": True})
step().status(503).body({"error": "down"}).headers([("Retry-After", "5")])
step().status(204)   # no body
```

---

## pytest fixture pattern

```python
import pytest
from mimicker.mimicker import mimicker, get, post


@pytest.fixture(scope="session")
def mock_server():
    server = mimicker(0).routes(
        get("/users/1").status(200).body({"id": 1, "name": "Alice"}),
        post("/users").status(201).body({"created": True}),
    )
    yield server
    server.shutdown()


def test_get_user(mock_server):
    import requests
    resp = requests.get(f"http://localhost:{mock_server.get_port()}/users/1")
    assert resp.json()["name"] == "Alice"
```

!!! tip "scope='session'"
    Using `scope="session"` starts Mimicker once per test session. Use `scope="function"` if your tests modify stubs between runs.

---

## Related

- [Stubbing Guide](../guides/stubbing-guide.md)
- [Dynamic Responses](../guides/dynamic-responses.md)
- [Stub File Schema](stub-file-schema.md)
- [CLI Reference](cli-reference.md)
