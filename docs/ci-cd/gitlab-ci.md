# GitLab CI

Use the Mimicker GitLab CI Catalog component to spin up a mock server in any pipeline job — no Python required.

---

## Usage

```yaml
# .gitlab-ci.yml
include:
  - component: gitlab.com/mimickerhq/mimicker-component/serve@1.0
    inputs:
      stubs_file: test/stubs.yaml   # optional
      port: 8080

test:
  extends: .mimicker-serve
  script:
    - pytest
  variables:
    MOCK_URL: http://localhost:8080
```

The component's `before_script` starts Mimicker and blocks until `/__mimicker__/health` returns 200. Your `script` runs after the server is confirmed healthy.

---

## Component inputs

| Input | Default | Description |
|---|---|---|
| `stubs_file` | _(none)_ | Path to a YAML stub file relative to the repo root |
| `port` | `8080` | Port to expose |
| `version` | `latest` | Mimicker image tag |
| `timeout` | `30` | Seconds to wait for healthy status |

---

## Without the component (Docker directly)

```yaml
test:
  image: docker:24
  services:
    - docker:24-dind
  before_script:
    - |
      docker run -d \
        --name mimicker \
        --network host \
        -v "$CI_PROJECT_DIR/test/stubs.yaml:/config/stubs.yaml:ro" \
        ghcr.io/mimickerhq/mimicker:latest

      # Wait for health
      elapsed=0
      until curl -sf http://localhost:8080/__mimicker__/health; do
        sleep 1
        elapsed=$((elapsed + 1))
        [ "$elapsed" -ge 30 ] && { docker logs mimicker; exit 1; }
      done
  script:
    - pytest
  after_script:
    - docker stop mimicker || true
```

---

## Stub coverage in GitLab

After your tests run, fetch the coverage report:

```yaml
test:
  extends: .mimicker-serve
  script:
    - pytest
    - mimicker report --url http://localhost:8080 --format text
    - mimicker report --url http://localhost:8080 --fail-on-unmatched
```

See [Stub Coverage Reports](stub-coverage-reports.md) for full details.

---

## Component source

The component source lives in [`contrib/gitlab-component/`](https://github.com/mimickerhq/mimicker/tree/main/contrib/gitlab-component) and is published at `gitlab.com/mimickerhq/mimicker-component`.

---

## Related

- [GitHub Actions](github-actions.md)
- [Docker](docker.md)
- [docker-compose](docker-compose.md)
- [Stub Coverage Reports](stub-coverage-reports.md)
