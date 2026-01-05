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
    vim \
    batcat \
 && rm -rf /var/lib/apt/lists/*

# install uv 
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# install just

RUN curl --proto 'https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

RUN useradd -m -s /bin/bash vscode
USER vscode
WORKDIR /workspace

# RUN pip install --user uv


# ENV PATH="/home/vscode/.local/bin:${PATH}"
