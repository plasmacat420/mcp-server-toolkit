# ── Stage 1: build wheel ──────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY client/ ./client/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir build \
    && python -m build --wheel --outdir /dist

# ── Stage 2: lean runtime image ───────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install the pre-built wheel (no build tools needed in the final image)
COPY --from=builder /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy source so editable paths (client/) remain importable
COPY src/ ./src/
COPY client/ ./client/

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

ENV TRANSPORT=stdio
ENV ROOT_DIR=/app/data

ENTRYPOINT ["mcp-toolkit"]
