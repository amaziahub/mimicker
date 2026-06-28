# Installation

## Requirements

Mimicker supports **Python 3.7 and above**. It has no required third-party runtime dependencies.

!!! note "Runtime vs. docs dependencies"
    `mkdocs-material` and `pymdown-extensions` are docs-only dependencies. They are never installed when users run `pip install mimicker`.

---

## Install from PyPI

=== "pip"

    ```bash
    pip install mimicker
    ```

=== "poetry"

    ```bash
    poetry add mimicker
    ```

=== "uv"

    ```bash
    uv add mimicker
    ```

---

## Verify the install

```bash
mimicker --help
```

You should see the Mimicker CLI help:

```
usage: mimicker [-h] {serve,wait,validate,report} ...

Mimicker — lightweight HTTP mock server
```

---

## Docker (no Python required)

If you're running Mimicker in CI without a Python environment, pull the official image:

```bash
docker pull ghcr.io/amaziahub/mimicker:latest
docker run -p 8080:8080 ghcr.io/amaziahub/mimicker:latest
```

See the [Docker guide](../ci-cd/docker.md) for full details.

---

## Next

→ [Quickstart](quickstart.md)
