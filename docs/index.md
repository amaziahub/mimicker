# Mimicker

**Lightweight Python-native HTTP mock server — for tests and CI alike.**

Mimicker lets you stub HTTP endpoints in seconds. Define stubs in Python, YAML, or from the CLI — no code required for CI-only users.

[![Mimicker Tests](https://github.com/mimickerhq/mimicker/actions/workflows/test.yml/badge.svg)](https://github.com/mimickerhq/mimicker/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/mimicker.svg)](https://pypi.org/project/mimicker/)
[![Downloads](https://pepy.tech/badge/mimicker)](https://pepy.tech/project/mimicker)
[![License](http://img.shields.io/:license-apache2.0-red.svg)](http://doge.mit-license.org)

---

## The pitch in one example

The same stub, three ways — pick whichever fits your workflow:

=== "YAML"

    ```yaml
    # stubs.yaml
    routes:
      - method: GET
        path: /hello
        status: 200
        body:
          message: Hello, World!
    ```

    ```bash
    mimicker serve --config stubs.yaml
    ```

=== "Python"

    ```python
    from mimicker.mimicker import mimicker, get

    mimicker(8080).routes(
        get("/hello").status(200).body({"message": "Hello, World!"})
    )
    ```

=== "CLI (inline)"

    ```bash
    mimicker serve --stub 'GET /hello -> 200 {"message": "Hello, World!"}'
    ```

---

## Key features

| Feature | Description |
|---|---|
| **Zero runtime deps** | No third-party packages needed to run mimicker in your tests |
| **Python DSL** | Fluent builder API — `get("/path").status(200).body({...})` |
| **YAML / JSON config** | Declarative stubs — no Python required for CI pipelines |
| **CLI** | `mimicker serve / wait / validate / report` |
| **Docker image** | `ghcr.io/mimickerhq/mimicker` — mount a YAML file and go |
| **Sequence responses** | Return different responses on successive calls |
| **Rate limiting** | Simulate 429 responses with configurable windows |
| **Dynamic responses** | `response_func` computes the response from request data |
| **Stub coverage** | Track which stubs were hit; catch contract drift in CI |
| **Health endpoint** | `/__mimicker__/health` built-in — no config needed |

---

## Install

```bash
pip install mimicker
```

---

## Next steps

- [**Quickstart →**](getting-started/quickstart.md) — running server in 30 seconds
- [**Stubbing Guide →**](guides/stubbing-guide.md) — YAML, Python, and CLI side-by-side
- [**Docker →**](ci-cd/docker.md) — run in CI without Python
- [**GitHub Actions →**](ci-cd/github-actions.md) — one-step integration
