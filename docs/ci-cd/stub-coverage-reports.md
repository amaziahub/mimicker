# Stub Coverage Reports

After your tests run, Mimicker knows exactly which stubs were exercised and which real requests hit no stub. Use this to catch **contract drift** — when your code calls endpoints you haven't mocked.

---

## What the report contains

Every running Mimicker server tracks:

- **Hit count** per stub (how many times each stub was matched)
- **Unused stubs** (stubs that were never called)
- **Unmatched requests** (requests that matched no stub — potential contract drift)

Fetch the report at any time:

```bash
GET /__mimicker__/report
```

---

## CLI report formats

=== "Text (default)"

    ```bash
    mimicker report --url http://localhost:8080
    ```

    ```
    Mimicker Report
      Stubs      : 2/3 exercised
      Unmatched  : 1 request(s)

    Unused stubs (never hit):
      - GET /api/users

    Unmatched requests (contract drift):
      - GET /api/accounts  [2024-01-15T10:30:00Z]
    ```

=== "JSON"

    ```bash
    mimicker report --url http://localhost:8080 --format json
    ```

    ```json
    {
      "summary": {
        "total_stubs": 3,
        "matched_stubs": 2,
        "unmatched_requests": 1
      },
      "stubs": [
        {"method": "GET", "path": "/api/orders", "hit_count": 3},
        {"method": "GET", "path": "/api/users",  "hit_count": 0},
        {"method": "POST", "path": "/api/orders", "hit_count": 1}
      ],
      "unused_stubs": [
        {"method": "GET", "path": "/api/users"}
      ],
      "unmatched_requests": [
        {"method": "GET", "path": "/api/accounts", "timestamp": "2024-01-15T10:30:00Z"}
      ]
    }
    ```

=== "GitHub Summary"

    ```bash
    mimicker report --url http://localhost:8080 --format github-summary
    ```

    Posts a Markdown table to `$GITHUB_STEP_SUMMARY`:

    ```markdown
    ## Mimicker Stub Coverage

    ✅ **2/3** stubs exercised &nbsp;|&nbsp; **1** unmatched request(s)

    ### Stub Coverage

    | Method | Path | Hits |
    |--------|------|-----:|
    | `GET` | `/api/orders` | ✅ 3 |
    | `GET` | `/api/users` | ❌ 0 |
    | `POST` | `/api/orders` | ✅ 1 |

    ### Unmatched Requests (Contract Drift)

    | Method | Path | Timestamp |
    |--------|------|-----------|
    | `GET` | `/api/accounts` | 2024-01-15T10:30:00Z |
    ```

---

## CI gate: fail on unmatched

```bash
mimicker report --fail-on-unmatched
```

Exits with code `1` if any requests were unmatched. Use this to turn contract drift into a hard CI failure.

---

## GitHub Actions integration

```yaml
- uses: amaziahub/mimicker-action@v1
  id: mimicker
  with:
    stubs: ./test/stubs.yaml

- name: Run tests
  run: pytest

- uses: amaziahub/mimicker-action/report@v1
  if: always()
  with:
    url: ${{ steps.mimicker.outputs.url }}
    fail_on_unmatched: true
```

See [GitHub Actions](github-actions.md) for the full workflow.

---

## Validate stubs before running tests

```bash
mimicker validate stubs.yaml && mimicker serve --config stubs.yaml
```

`mimicker validate` exits `0` for a valid file and `1` for any error — use it as a pre-commit check or CI lint step.

---

## Related

- [CLI Reference](../reference/cli-reference.md) — full `mimicker report` options
- [GitHub Actions](github-actions.md)
- [GitLab CI](gitlab-ci.md)
- [Docker](docker.md)
