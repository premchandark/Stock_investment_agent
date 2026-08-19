# Multi-stage build following the OpenEnv base image pattern
FROM ghcr.io/meta-pytorch/openenv-base:latest AS builder

WORKDIR /app

COPY . /app/env

WORKDIR /app/env

# Ensure uv and git are available
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && if ! command -v uv >/dev/null 2>&1; then \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        install -m 0755 /root/.local/bin/uv /usr/local/bin/uv && \
        install -m 0755 /root/.local/bin/uvx /usr/local/bin/uvx; \
    fi

# Install dependencies (two-phase: deps first, then project)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-editable

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-editable

# Final runtime stage
FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app

COPY --from=builder /app/env/.venv /app/.venv
COPY --from=builder /app/env /app/env

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/env:$PYTHONPATH"
ENV ENABLE_WEB_INTERFACE=true

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:8000/health'); assert json.loads(r.read())['status']=='healthy'" || exit 1

CMD ["sh", "-c", "cd /app/env && uvicorn server.app:app --host 0.0.0.0 --port 8000"]
