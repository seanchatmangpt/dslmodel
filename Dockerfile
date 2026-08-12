# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.12.12
FROM python:${PYTHON_VERSION}-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system dslmodel && useradd --system --gid dslmodel --create-home dslmodel
WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install . && \
    python -m pip check && \
    dsl doctor --json --strict > /tmp/dslmodel-doctor.json && \
    dsl dsl status --json --strict > /tmp/dslmodel-status.json

USER dslmodel
ENTRYPOINT ["dsl"]
CMD ["--help"]
