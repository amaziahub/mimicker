# Docker

Run Mimicker in any CI environment — no Python installation required.

## Image

```
ghcr.io/mimickerhq/mimicker:latest
```

Multi-arch: `linux/amd64` and `linux/arm64`. Non-root user. Automatic health check built in.

---

## Quickstart

```bash
# Start with no stubs (returns 404 for all paths)
docker run -p 8080:8080 ghcr.io/mimickerhq/mimicker:latest

# Mount a stubs file (auto-loaded from /config/stubs.yaml)
docker run -p 8080:8080 \
  -v ./stubs.yaml:/config/stubs.yaml:ro \
  ghcr.io/mimickerhq/mimicker:latest
```

The image auto-loads `/config/stubs.yaml` when present — no `--config` flag needed.

---

## Custom port

```bash
docker run -e MIMICKER_PORT=9090 -p 9090:9090 ghcr.io/mimickerhq/mimicker:latest
```

Setting `MIMICKER_PORT` also keeps the built-in `HEALTHCHECK` pointing at the right port.

---

## Health check

Every Mimicker container exposes a health endpoint:

```
GET /__mimicker__/health
→ 200 {"status": "up"}
```

The image includes a Docker `HEALTHCHECK` that polls this endpoint automatically. You can use it in `docker-compose`, Kubernetes readiness probes, or CI scripts without any extra configuration.

Wait for the container to be healthy before running tests:

```bash
docker run -d --name mock -p 8080:8080 \
  -v ./stubs.yaml:/config/stubs.yaml:ro \
  ghcr.io/mimickerhq/mimicker:latest

# Block until healthy
mimicker wait --url http://localhost:8080 --timeout 30
```

Or use pure shell (no mimicker CLI needed):

```bash
until curl -sf http://localhost:8080/__mimicker__/health; do sleep 1; done
```

---

## Other CLI subcommands in Docker

```bash
# Validate a stubs file without starting a server
docker run --rm \
  -v ./stubs.yaml:/config/stubs.yaml:ro \
  ghcr.io/mimickerhq/mimicker:latest \
  validate /config/stubs.yaml

# Fetch the stub coverage report from a running container
docker exec mock mimicker report --format text
```

---

## Related

- [docker-compose](docker-compose.md) — service dependency health gates
- [GitHub Actions](github-actions.md)
- [GitLab CI](gitlab-ci.md)
- [Stub Coverage Reports](stub-coverage-reports.md)
