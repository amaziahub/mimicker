# Path & Query Parameters

Mimicker supports dynamic path variables and query string matching out of the box.

---

## Path parameters

Use `{variable}` syntax in the path. The variable is automatically injected into the response body wherever the same placeholder appears.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /users/{id}
        status: 200
        body:
          id: "{id}"
          name: Alice
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get

    mimicker(8080).routes(
        get("/users/{id}")
        .status(200)
        .body({"id": "{id}", "name": "Alice"})
    )
    ```

```bash
curl http://localhost:8080/users/42
# {"id": "42", "name": "Alice"}
```

Multiple path parameters work the same way:

```python
mimicker(8080).routes(
    get("/orgs/{org}/repos/{repo}")
    .status(200)
    .body({"org": "{org}", "repo": "{repo}"})
)
```

---

## Query parameters — explicit

Define query parameters directly in the path template. Only requests that include the exact parameter are matched.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /search
        query_params:
          q: python
        status: 200
        body:
          results: []
    ```

=== "Python"

    ```python
    mimicker(8080).routes(
        get("/search?q={term}")
        .status(200)
        .body({"results": [], "term": "{term}"})
    )
    ```

```bash
curl "http://localhost:8080/search?q=python"
# {"results": [], "term": "python"}
```

---

## Query parameters — implicit (wildcard)

When a path template has **no** query string, Mimicker matches any request to that path regardless of what query parameters are present. The parameters are still available in `response_func` via `kwargs["query_params"]`.

```python
mimicker(8080).routes(
    get("/hello")
    .status(200)
    .body({"message": "Hello!"})
)

# GET /hello              → 200 ✓
# GET /hello?name=bob     → 200 ✓  (parameters ignored but available in response_func)
# GET /hello?x=1&y=2      → 200 ✓
```

Access implicit parameters in a dynamic response:

```python
from typing import Dict, List

def greet(**kwargs):
    query_params: Dict[str, List[str]] = kwargs["query_params"]
    name = query_params.get("name", ["World"])[0]
    return 200, {"message": f"Hello, {name}!"}

mimicker(8080).routes(
    get("/hello").response_func(greet)
)
```

!!! note "Query params are always lists"
    Because HTTP allows repeated parameters (`?tag=a&tag=b`), `query_params` values are always `List[str]`. Use `[0]` to get the first value.

---

## Path params in `response_func`

Path variables are available as `kwargs["params"]`:

```python
def user_detail(**kwargs):
    user_id = kwargs["params"]["id"]
    return 200, {"id": user_id, "name": f"User {user_id}"}

mimicker(8080).routes(
    get("/users/{id}").response_func(user_detail)
)
```

---

## Related

- [Dynamic Responses](dynamic-responses.md) — full `response_func` reference
- [Stubbing Guide](stubbing-guide.md)
