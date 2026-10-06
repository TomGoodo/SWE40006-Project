FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies first so this layer is cached until the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Then copy the source and install the project itself
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]
