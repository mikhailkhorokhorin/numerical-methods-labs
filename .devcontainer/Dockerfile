FROM mcr.microsoft.com/devcontainers/base:trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
        python3 \
        python3-venv \
        python3-pytest \
        python3-pytest-cov \
        mypy \
        pre-commit \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory '*'
