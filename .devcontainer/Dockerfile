FROM python:3.11-slim

# ========== SYSTEM SETUP ==========
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/home/vscode/.cache/uv

RUN apt-get update && apt-get install -y \
    curl \
    git \
    bash \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash vscode
USER vscode
WORKDIR /workspace

RUN pip install --user uv


ENV PATH="/home/vscode/.local/bin:${PATH}"
