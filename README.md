<p align="center">
  <img src="https://raw.githubusercontent.com/amaziahub/mimicker/main/mimicker.jpg" alt="Mimicker logo" 
       style="width: 200px; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border: 2px solid black;">
</p>

<div align="center">

> **Mimicker** – Your lightweight, Python-native HTTP mocking server.

</div>

<div align="center">

[![Mimicker Tests](https://github.com/amaziahub/mimicker/actions/workflows/test.yml/badge.svg)](https://github.com/amaziahub/mimicker/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/mimicker.svg)](https://pypi.org/project/mimicker/)
[![Downloads](https://pepy.tech/badge/mimicker)](https://pepy.tech/project/mimicker)
[![Last Commit](https://img.shields.io/github/last-commit/amaziahub/mimicker.svg)](https://github.com/amaziahub/mimicker/commits/main)
[![Codecov Coverage](https://codecov.io/gh/amaziahub/mimicker/branch/main/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/amaziahub/mimicker)
[![License](http://img.shields.io/:license-apache2.0-red.svg)](http://doge.mit-license.org)
![Poetry](https://img.shields.io/badge/managed%20with-poetry-blue)

</div>

---

Mimicker is a Python-native HTTP mocking server — no third-party runtime dependencies, ideal for integration tests and CI.

## Quick example

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello").status(200).body({"message": "Hello, World!"})
)
```

Or use a YAML config file — no Python needed:

```yaml
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

## Install

```bash
pip install mimicker
```

## Documentation

Full docs at **[amaziahub.github.io/mimicker](https://amaziahub.github.io/mimicker)**

- [Quickstart](https://amaziahub.github.io/mimicker/getting-started/quickstart/)
- [Stubbing Guide](https://amaziahub.github.io/mimicker/guides/stubbing-guide/) — YAML, Python, and CLI side-by-side
- [Path & Query Params](https://amaziahub.github.io/mimicker/guides/path-and-query-params/)
- [Dynamic Responses](https://amaziahub.github.io/mimicker/guides/dynamic-responses/)
- [Docker](https://amaziahub.github.io/mimicker/ci-cd/docker/)
- [GitHub Actions](https://amaziahub.github.io/mimicker/ci-cd/github-actions/)
- [CLI Reference](https://amaziahub.github.io/mimicker/reference/cli-reference/)
- [Python API](https://amaziahub.github.io/mimicker/reference/python-api/)

## Community

- [Slack](https://join.slack.com/t/mimicker/shared_invite/zt-2yr7vubw4-8Y09YyxZ5j~G2tlQ5uOXKw)
- [Issues](https://github.com/amaziahub/mimicker/issues)
