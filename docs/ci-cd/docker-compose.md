# docker-compose

Use Mimicker as a service dependency in docker-compose. The `service_healthy` condition ensures your application only starts once Mimicker is ready.

---

## Basic example

```yaml
# docker-compose.yml
services:
  mimicker:
    image: ghcr.io/mimickerhq/mimicker:latest
    ports:
      - "8080:8080"
    volumes:
      - ./stubs.yaml:/config/stubs.yaml:ro
    healthcheck:
      test: ["CMD", "mimicker", "wait", "--url", "http://localhost:8080", "--timeout", "2"]
      interval: 2s
      timeout: 3s
      retries: 5
      start_period: 3s

  myapp:
    image: myapp:latest
    depends_on:
      mimicker:
        condition: service_healthy   # myapp waits until Mimicker passes health checks
    environment:
      DOWNSTREAM_URL: http://mimicker:8080
```

```bash
docker compose up
```

---

## Custom port

```yaml
services:
  mimicker:
    image: ghcr.io/mimickerhq/mimicker:latest
    environment:
      MIMICKER_PORT: "9090"
    ports:
      - "9090:9090"
```

Setting `MIMICKER_PORT` keeps the built-in `HEALTHCHECK` pointing at the right port — no other changes needed.

---

## Inline stubs (no file)

```yaml
services:
  mimicker:
    image: ghcr.io/mimickerhq/mimicker:latest
    command: serve --stub 'GET /ping -> 200 {"ok": true}'
    ports:
      - "8080:8080"
```

---

## Test runner integration

```yaml
services:
  mimicker:
    image: ghcr.io/mimickerhq/mimicker:latest
    volumes:
      - ./test/stubs.yaml:/config/stubs.yaml:ro
    healthcheck:
      test: ["CMD", "mimicker", "wait", "--url", "http://localhost:8080", "--timeout", "2"]
      interval: 2s
      timeout: 3s
      retries: 5

  tests:
    build: .
    command: pytest
    depends_on:
      mimicker:
        condition: service_healthy
    environment:
      MOCK_URL: http://mimicker:8080
```

```bash
docker compose run tests
```

---

## Related

- [Docker](docker.md) — image details and options
- [GitHub Actions](github-actions.md)
- [GitLab CI](gitlab-ci.md)
- [Stub Coverage Reports](stub-coverage-reports.md)
