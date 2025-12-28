FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1

ENV UV_LINK_MODE=copy

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock ./.python-version /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY ./app /app/app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV FASTAPI_PORT=8000
EXPOSE 8000
CMD ["uvicorn", "dev", "app/main.py", "host", "0.0.0.0", "--port", "8000"]

