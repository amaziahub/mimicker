# Stub File Schema

Complete reference for the YAML (and JSON) stub config format accepted by `mimicker serve --config` and `server.load_config()`.

---

## Top-level structure

```yaml
port: 8080        # optional — overrides --port flag
routes:           # required — list of route objects
  - ...
```

| Field | Type | Required | Description |
|---|---|---|---|
| `port` | integer | No | Port for the server to listen on |
| `routes` | list | Yes | One or more route definitions |

---

## Route fields

```yaml
routes:
  - method: GET            # required
    path: /users/{id}      # required
    status: 200            # required (unless sequence is set)
    body: ...              # optional
    headers: {}            # optional
    delay_ms: 0            # optional
    sequence: []           # optional — overrides status/body
    cycle: false           # optional — only with sequence
```

| Field | Type | Default | Description |
|---|---|---|---|
| `method` | string | required | HTTP method: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS` |
| `path` | string | required | URL path, supports `{variable}` placeholders |
| `status` | integer | required¹ | HTTP status code |
| `body` | any | `""` | Response body — object, list, string, or number |
| `headers` | object | `{}` | Response headers as key-value pairs |
| `delay_ms` | integer | `0` | Artificial delay in milliseconds |
| `sequence` | list | — | List of sequence step objects; overrides `status`/`body` |
| `cycle` | boolean | `false` | If `true`, sequence wraps around instead of repeating last step |

¹ Required unless `sequence` is provided.

---

## Body types

```yaml
# Object → application/json
body:
  id: 1
  name: Alice

# List → application/json
body:
  - 1
  - 2

# String → text/plain
body: "plain text response"

# Number
body: 42

# Empty body (no body field, or explicit empty)
body: ""

# Path param interpolation
# Any {varname} in the body string is replaced with the actual path value
body:
  id: "{id}"
  message: "Found user {id}"
```

---

## Headers

```yaml
routes:
  - method: GET
    path: /secure
    status: 200
    headers:
      Content-Type: application/json
      X-Custom-Header: my-value
      Cache-Control: no-cache
    body:
      ok: true
```

---

## Delay

```yaml
routes:
  - method: GET
    path: /slow
    status: 200
    delay_ms: 500   # 500ms — good for testing timeout handling
    body:
      result: ok
```

---

## Sequence

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

After the last step, the server repeats the final step unless `cycle: true`:

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

### Sequence step fields

| Field | Type | Default | Description |
|---|---|---|---|
| `status` | integer | required | HTTP status for this step |
| `body` | any | `""` | Response body for this step |
| `headers` | object | `{}` | Response headers for this step |
| `delay_ms` | integer | `0` | Delay for this step |

---

## Path parameters

```yaml
routes:
  - method: GET
    path: /users/{id}
    status: 200
    body:
      id: "{id}"
      name: user-{id}
```

`{id}` is replaced with the actual value from the request URL in the response body.

---

## Complete example

```yaml
port: 8080

routes:
  # Simple GET
  - method: GET
    path: /health
    status: 200
    body:
      status: ok

  # Dynamic path parameter
  - method: GET
    path: /users/{id}
    status: 200
    body:
      id: "{id}"
      name: Alice

  # POST with custom header and delay
  - method: POST
    path: /orders
    status: 201
    headers:
      Location: /orders/1
    delay_ms: 100
    body:
      order_id: 1
      created: true

  # Sequence (flaky endpoint)
  - method: GET
    path: /unstable
    cycle: true
    sequence:
      - status: 200
        body: {ok: true}
      - status: 500
        body: {error: internal error}

  # No body (204 No Content)
  - method: DELETE
    path: /items/{id}
    status: 204
```

---

## JSON format

The same structure works as JSON:

```json
{
  "port": 8080,
  "routes": [
    {
      "method": "GET",
      "path": "/health",
      "status": 200,
      "body": {"status": "ok"}
    }
  ]
}
```

---

## Related

- [CLI Reference](cli-reference.md) — `mimicker serve`, `validate`, `report`
- [Stubbing Guide](../guides/stubbing-guide.md) — YAML/Python/CLI side-by-side
- [Python API](python-api.md) — programmatic stub building
