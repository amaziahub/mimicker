# Dynamic Responses

`response_func` lets you compute the response at request time — inspect the request body, headers, path parameters, or query string and return any status code and body.

---

## Basic usage

```python
from mimicker.mimicker import mimicker, post

def greet(**kwargs):
    payload = kwargs.get("payload") or {}
    name = payload.get("name", "Guest")
    return 200, {"message": f"Hello, {name}!"}

mimicker(8080).routes(
    post("/greet").response_func(greet)
)
```

```bash
curl -X POST http://localhost:8080/greet -d '{"name": "World"}' -H 'Content-Type: application/json'
# {"message": "Hello, World!"}

curl -X POST http://localhost:8080/greet
# {"message": "Hello, Guest!"}
```

---

## Available kwargs

| Key | Type | Description |
|---|---|---|
| `payload` | `dict \| None` | Parsed JSON request body (None if no body or not JSON) |
| `headers` | `dict[str, str]` | Lowercased request headers |
| `params` | `dict[str, str]` | Path parameter values (e.g. `{"id": "42"}`) |
| `query_params` | `dict[str, list[str]]` | Query string parameters (always lists) |

---

## Examples

### Inspect request headers

```python
def auth_check(**kwargs):
    token = kwargs["headers"].get("authorization", "")
    if token == "Bearer secret":
        return 200, {"authorized": True}
    return 401, {"error": "Unauthorized"}

mimicker(8080).routes(
    get("/protected").response_func(auth_check)
)
```

### Echo path parameters

```python
def echo_id(**kwargs):
    user_id = kwargs["params"]["id"]
    return 200, {"id": user_id, "fetched": True}

mimicker(8080).routes(
    get("/users/{id}").response_func(echo_id)
)
```

### Use query parameters

```python
def search(**kwargs):
    q = kwargs["query_params"].get("q", [""])[0]
    return 200, {"query": q, "results": []}

mimicker(8080).routes(
    get("/search").response_func(search)
)
```

### Simulate conditional errors

```python
def flaky_api(**kwargs):
    import random
    if random.random() < 0.3:
        return 503, {"error": "service unavailable"}
    return 200, {"data": "ok"}

mimicker(8080).routes(
    get("/api/data").response_func(flaky_api)
)
```

---

## Combining with delay

`response_func` and `.delay()` can be combined on the same route:

```python
mimicker(8080).routes(
    get("/slow").delay(0.5).response_func(my_func)
)
```

!!! note "response_func vs sequence"
    Use `response_func` when the response depends on the **request content**. Use `sequence` (see [Stubbing Guide](stubbing-guide.md)) when the response depends on the **call count** — they serve different purposes.

---

## Related

- [Path & Query Params](path-and-query-params.md)
- [Stubbing Guide](stubbing-guide.md)
- [Python API](../reference/python-api.md)
