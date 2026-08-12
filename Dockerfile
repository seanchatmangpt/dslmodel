# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.12.12

FROM python:${PYTHON_VERSION}-slim AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip wheel --wheel-dir /wheels .

FROM python:${PYTHON_VERSION}-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system dslmodel && useradd --system --gid dslmodel --create-home dslmodel
WORKDIR /app

# Only built distribution artifacts cross the builder/runtime boundary. Historical
# repository source is never copied into the production image.
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-index --find-links=/wheels dslmodel && \
    rm -rf /wheels && \
    python -m pip check && \
    dsl doctor --json --strict > /tmp/dslmodel-doctor.json && \
    dsl dsl status --json --strict > /tmp/dslmodel-status.json && \
    python -c 'import importlib.util as i; assert i.find_spec("dslmodel.verbs"); assert i.find_spec("dslmodel.pqc.algorithms"); assert i.find_spec("dslmodel.evolution") is None; assert i.find_spec("dslmodel.commands.swarm") is None'

USER dslmodel
ENTRYPOINT ["dsl"]
CMD ["--help"]
