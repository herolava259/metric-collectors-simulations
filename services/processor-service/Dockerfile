
FROM ghcr.io/astral-sh/uv:latest AS uv_setup


WORKDIR /app


COPY pyproject.toml ./

RUN uv pip install --no-cache -r pyproject.toml --target /app/packages


FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=uv_setup /app/packages /usr/local/lib/python3.10/site-packages

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages


RUN adduser --disabled-password appuser
USER appuser

# Lệnh chạy Worker xử lý dữ liệu [cite: 15]
CMD ["python", "main.py"]