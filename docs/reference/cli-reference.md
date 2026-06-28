# CLI Reference

Mimicker ships a `mimicker` CLI so any CI pipeline can control it without writing Python.

Install:

```bash
pip install mimicker
# or: docker run ghcr.io/mimickerhq/mimicker ...
```

---

## `mimicker serve`

Start the mock server.

```
mimicker serve [--port PORT] [--config FILE] [--stub STUB]
```

| Flag | Default | Description |
|---|---|---|
| `--port PORT` | `8080` | Port to listen on. Overridden by `port:` in config file if present. |
| `--config FILE` | _(auto-detect)_ | YAML or JSON stub config file. Auto-loaded from `/config/stubs.yaml` if present. |
| `--stub STUB` | _(none)_ | Inline stub: `'METHOD /path -> STATUS {json}'` |

**Examples:**

```bash
# From a config file
mimicker serve --config stubs.yaml

# From a config file on a custom port
mimicker serve --config stubs.yaml --port 9090

# Inline one-liner
mimicker serve --stub 'GET /ping -> 200 {"ok": true}'

# Docker: auto-loads /config/stubs.yaml
docker run -p 8080:8080 \
  -v ./stubs.yaml:/config/stubs.yaml:ro \
  ghcr.io/mimickerhq/mimicker:latest
```

!!! tip "Environment variable port"
    In Docker, set `MIMICKER_PORT=9090` instead of overriding the CMD — the health check follows automatically.

---

## `mimicker wait`

Block until the server's health endpoint returns 200. Useful in CI scripts and `before_script` blocks.

```
mimicker wait [--url URL] [--timeout SECONDS]
```

| Flag | Default | Description |
|---|---|---|
| `--url URL` | `http://localhost:8080` | Server base URL |
| `--timeout SECONDS` | `10.0` | Maximum time to wait |

**Examples:**

```bash
# Wait up to 30 seconds
mimicker wait --url http://localhost:8080 --timeout 30

# In CI: fail the build if server doesn't start in time
mimicker wait --url http://localhost:9090 --timeout 15 || exit 1
```

Exits `0` when the server is ready, `1` on timeout.

---

## `mimicker validate`

Validate a stub config file without starting a server. Use as a pre-commit check or CI lint step.

```
mimicker validate FILE
```

**Examples:**

```bash
mimicker validate stubs.yaml
# [OK] stubs.yaml is valid (3 route(s) defined)

mimicker validate bad.yaml
# [ERROR] routes[0]: invalid method 'FETCH'. Must be one of ['DELETE', 'GET', ...]
# exit code: 1
```

Exits `0` for a valid file, `1` for any error.

---

## `mimicker report`

Fetch and display the stub coverage and request-drift report from a running server.

```
mimicker report [--url URL] [--format FORMAT] [--fail-on-unmatched]
```

| Flag | Default | Description |
|---|---|---|
| `--url URL` | `http://localhost:8080` | Server base URL |
| `--format FORMAT` | `text` | Output format: `text`, `json`, `github-summary` |
| `--fail-on-unmatched` | off | Exit `1` if any requests were unmatched |

**Examples:**

```bash
# Human-readable text
mimicker report

# Machine-readable JSON
mimicker report --format json

# GitHub Actions job summary (Markdown table)
mimicker report --format github-summary >> $GITHUB_STEP_SUMMARY

# Fail CI on contract drift
mimicker report --fail-on-unmatched
```

See [Stub Coverage Reports](../ci-cd/stub-coverage-reports.md) for output examples.

---

## Inline stub syntax

The `--stub` flag accepts a compact one-liner:

```
METHOD /path -> STATUS [json_body]
```

```bash
# No body
mimicker serve --stub 'DELETE /items/1 -> 204'

# JSON body
mimicker serve --stub 'POST /users -> 201 {"id": 99, "created": true}'

# With spaces in the path
mimicker serve --stub 'GET /api/v1/health -> 200 {"status": "up"}'
```

For more complex stubs (headers, delays, sequences, multiple routes), use a config file.

---

## Related

- [Stub File Schema](stub-file-schema.md)
- [Stub Coverage Reports](../ci-cd/stub-coverage-reports.md)
- [Docker](../ci-cd/docker.md)
