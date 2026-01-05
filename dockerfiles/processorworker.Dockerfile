FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder 
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

ARG SRC_PATH=services/processor-service
ARG LIB_PATH=common/packages

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=${SRC_PATH}/pyproject.toml,target=${SRC_PATH}/pyproject.toml \
    --mount=type=bind,source=${LIB_PATH}/metric-ingestion,target=${LIB_PATH}/metric-ingestion \
    --mount=type=bind,source=${LIB_PATH}/metric-ingestion-models,target=${LIB_PATH}/metric-ingestion-models \
    uv sync --frozen --no-install-project --no-dev --no-install-workspace --package processor-service

COPY uv.lock .
COPY pyproject.toml .
COPY ${LIB_PATH}/ ./${LIB_PATH}
COPY ${SRC_PATH}/ ./${SRC_PATH}

RUN ls -R

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package processor-service
# --frozen --no-dev --package package-service

FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/services/processor-service
CMD ["python", "main.py"]


