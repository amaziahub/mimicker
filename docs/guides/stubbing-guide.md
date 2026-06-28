# Stubbing Guide

The same stub can be defined three ways — pick whichever fits your workflow. No SDK is required for CI-only users.

---

## Defining a stub

=== "YAML"

    ```yaml
    # stubs.yaml
    routes:
      - method: GET
        path: /api/users/1
        status: 200
        body:
          id: 1
          name: Alice
          role: admin
    ```

    Start the server:

    ```bash
    mimicker serve --config stubs.yaml
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get

    mimicker(8080).routes(
        get("/api/users/1")
        .status(200)
        .body({"id": 1, "name": "Alice", "role": "admin"})
    )
    ```

=== "CLI (inline)"

    ```bash
    mimicker serve --stub 'GET /api/users/1 -> 200 {"id":1,"name":"Alice"}'
    ```

---

## HTTP methods

All standard HTTP methods are supported.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /items
        status: 200
        body:
          items: []

      - method: POST
        path: /items
        status: 201
        body:
          created: true

      - method: PUT
        path: /items/1
        status: 200
        body:
          updated: true

      - method: DELETE
        path: /items/1
        status: 204

      - method: PATCH
        path: /items/1
        status: 200
        body:
          patched: true
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get, post, put, delete, patch

    mimicker(8080).routes(
        get("/items").status(200).body({"items": []}),
        post("/items").status(201).body({"created": True}),
        put("/items/1").status(200).body({"updated": True}),
        delete("/items/1").status(204),
        patch("/items/1").status(200).body({"patched": True}),
    )
    ```

---

## Custom response headers

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /protected
        status: 200
        headers:
          X-Auth-Token: secret-token
          Content-Type: application/json
        body:
          data: ok
    ```

=== "Python"

    ```python
    mimicker(8080).routes(
        get("/protected")
        .status(200)
        .headers([("X-Auth-Token", "secret-token"), ("Content-Type", "application/json")])
        .body({"data": "ok"})
    )
    ```

---

## Response delay

Simulate slow APIs or test timeout handling.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /slow
        status: 200
        body:
          result: ok
        delay_ms: 500    # milliseconds
    ```

=== "Python"

    ```python
    mimicker(8080).routes(
        get("/slow").delay(0.5).status(200).body({"result": "ok"})
    )
    ```

!!! tip "Testing timeouts"
    Set `delay` longer than your client's timeout to reliably trigger `ReadTimeout` in tests.

---

## Sequence responses

Return a different response on each successive call — ideal for simulating retries, flaky services, or multi-step workflows.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /flaky
        sequence:
          - status: 200
            body:
              ok: true
          - status: 503
            body:
              error: service unavailable
          - status: 200
            body:
              ok: true
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get
    from mimicker.sequence import step

    mimicker(8080).routes(
        get("/flaky")
        .sequence(
            step().status(200).body({"ok": True}),
            step().status(503).body({"error": "service unavailable"}),
            step().status(200).body({"ok": True}),
        )
    )
    ```

After the last step, the final step repeats by default. Pass `cycle=True` to loop:

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /alternating
        cycle: true
        sequence:
          - status: 200
            body: {ok: true}
          - status: 500
            body: {error: boom}
    ```

=== "Python"

    ```python
    mimicker(8080).routes(
        get("/alternating")
        .sequence(
            step().status(200).body({"ok": True}),
            step().status(500).body({"error": "boom"}),
            cycle=True,
        )
    )
    # Requests alternate: 200, 500, 200, 500, ...
    ```

---

## Rate limiting

Simulate 429 Too Many Requests responses.

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /api/data
        status: 200
        body:
          data: ok
    ```

    Rate limiting is configured in Python only (not yet in the YAML schema).

=== "Python"

    ```python
    mimicker(8080).routes(
        get("/api/data")
        .status(200)
        .body({"data": "ok"})
        .rate_limit(max_requests=5, window_seconds=60)
    )
    # First 5 requests → 200
    # 6th+ request → 429 Too Many Requests
    ```

    Customize the 429 response:

    ```python
    mimicker(8080).routes(
        get("/api/data")
        .rate_limit(
            max_requests=5,
            window_seconds=60,
            status_code=429,
            body={"error": "rate_limit_exceeded", "retry_after": 60},
            headers=[("Retry-After", "60")],
        )
    )
    ```

    Per-client rate limiting via a header key:

    ```python
    mimicker(8080).routes(
        get("/api/users")
        .rate_limit(max_requests=10, window_seconds=60, key_header="X-Api-Key")
    )
    # Each unique X-Api-Key value has its own independent counter.
    ```

---

## Multiple routes

=== "YAML"

    ```yaml
    routes:
      - method: GET
        path: /health
        status: 200
        body:
          status: ok

      - method: GET
        path: /users/{id}
        status: 200
        body:
          id: "{id}"
          name: Alice

      - method: POST
        path: /orders
        status: 201
        body:
          order_id: 42
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get, post

    mimicker(8080).routes(
        get("/health").status(200).body({"status": "ok"}),
        get("/users/{id}").status(200).body({"id": "{id}", "name": "Alice"}),
        post("/orders").status(201).body({"order_id": 42}),
    )
    ```

---

## Loading YAML from Python

```python
server = mimicker(8080).load_config("stubs.yaml")
```

This is useful when you want to manage stubs in YAML but start the server from Python test fixtures.

---

## Related

- [Path & Query Params](path-and-query-params.md) — dynamic path variables and query string matching
- [Dynamic Responses](dynamic-responses.md) — compute responses from request data with `response_func`
- [Stub File Schema](../reference/stub-file-schema.md) — complete YAML/JSON field reference
- [Python API](../reference/python-api.md) — full method reference
