# Stage 1: build and install the package
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools
RUN pip install --no-cache-dir poetry==1.8.2

# Copy dependency manifests first for layer caching
COPY pyproject.toml poetry.lock ./

# Export runtime requirements and install them into /install
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy source and install the package itself
COPY mimicker/ ./mimicker/
COPY README.md ./
RUN pip install --no-cache-dir --prefix=/install --no-deps .


# Stage 2: lean runtime image
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/amaziahub/mimicker"
LABEL org.opencontainers.image.description="Lightweight Python-native HTTP mock server"
LABEL org.opencontainers.image.licenses="MIT"

# Non-root user
RUN groupadd --system mimicker && useradd --system --gid mimicker --no-create-home mimicker

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Entrypoint script — reads MIMICKER_PORT for the default serve command
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Convention: /config/stubs.yaml is the standard mount point for stubs.
# The CLI auto-loads it when present (no flag needed).
RUN mkdir -p /config && chown mimicker:mimicker /config

WORKDIR /config

USER mimicker

ENV MIMICKER_PORT=8080

# Health check reads MIMICKER_PORT so it works on any port
HEALTHCHECK --interval=2s --timeout=3s --start-period=3s --retries=5 \
    CMD mimicker wait --url http://localhost:${MIMICKER_PORT} --timeout 2

EXPOSE 8080

# With no CMD args:  mimicker serve --port ${MIMICKER_PORT}
# With CMD args:     mimicker <args>  (e.g. validate, report, wait)
# Change port:       docker run -e MIMICKER_PORT=9090 -p 9090:9090 ...
ENTRYPOINT ["docker-entrypoint.sh"]
