# GitHub Actions

Add Mimicker to any workflow in two lines. The action starts the server, waits until it's healthy, and exposes its URL as an output — your tests can start immediately.

---

## Basic usage

```yaml
steps:
  - uses: amaziahub/mimicker-action@v1
    id: mimicker
    with:
      stubs: ./test/stubs.yaml   # optional
      port: 8080

  - name: Run tests
    run: pytest
    env:
      MOCK_URL: ${{ steps.mimicker.outputs.url }}
```

The server is guaranteed healthy before the next step runs.

---

## Inputs

| Input | Default | Description |
|---|---|---|
| `stubs` | _(none)_ | Path to a YAML stub file to load |
| `port` | `8080` | Port to expose |
| `version` | `latest` | Mimicker Docker image tag |
| `timeout` | `30` | Seconds to wait for healthy status |

## Outputs

| Output | Description |
|---|---|
| `url` | Base URL of the running server, e.g. `http://localhost:8080` |

---

## Stub coverage report

Post a stub coverage summary to the GitHub Actions job summary after your tests run:

```yaml
steps:
  - uses: amaziahub/mimicker-action@v1
    id: mimicker
    with:
      stubs: ./test/stubs.yaml

  - name: Run tests
    run: pytest

  - uses: amaziahub/mimicker-action/report@v1
    if: always()   # run even if tests fail
    with:
      url: ${{ steps.mimicker.outputs.url }}
      fail_on_unmatched: true   # exit 1 if any requests hit no stub
```

The report action posts a Markdown table to `$GITHUB_STEP_SUMMARY`:

| Method | Path | Hits |
|--------|------|-----:|
| `GET` | `/api/orders` | ✅ 3 |
| `GET` | `/api/users` | ❌ 0 |

See [Stub Coverage Reports](stub-coverage-reports.md) for details.

---

## Without the action (Docker directly)

If you prefer not to use the composite action:

```yaml
services:
  mimicker:
    image: ghcr.io/amaziahub/mimicker:latest
    ports:
      - 8080:8080

steps:
  - name: Wait for Mimicker
    run: |
      until curl -sf http://localhost:8080/__mimicker__/health; do sleep 1; done

  - name: Run tests
    run: pytest
    env:
      MOCK_URL: http://localhost:8080
```

---

## Action source

The action source lives in [`contrib/github-action/`](https://github.com/amaziahub/mimicker/tree/main/contrib/github-action) and is published separately at [amaziahub/mimicker-action](https://github.com/amaziahub/mimicker-action).

---

## Related

- [docker-compose](docker-compose.md)
- [GitLab CI](gitlab-ci.md)
- [Stub Coverage Reports](stub-coverage-reports.md)
- [Docker](docker.md)
