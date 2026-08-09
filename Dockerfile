# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12
FROM python:$PYTHON_VERSION-slim AS base

# Remove docker-clean so we can keep the apt cache in Docker build cache.
RUN rm /etc/apt/apt.conf.d/docker-clean

# Create a non-root user and switch to it.
ARG UID=1000
ARG GID=$UID
RUN groupadd --gid $GID user && \
    useradd --create-home --gid $GID --uid $UID user --no-log-init && \
    chown user /opt/
USER user

ENV VIRTUAL_ENV=/opt/dslmodel-env
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN python -m venv $VIRTUAL_ENV

WORKDIR /workspaces/dslmodel/

# Legacy development target retained for reversible local use. Production does
# not depend on this stage or its broad historical dependency graph.
FROM base AS builder

USER root
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes build-essential curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

USER user
COPY --chown=user:user pyproject.toml uv.lock uv.toml /workspaces/dslmodel/
RUN mkdir -p src/dslmodel/ && touch src/dslmodel/__init__.py && touch README.md
RUN uv sync --frozen --active

FROM builder AS dev

USER root
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes git gnupg ssh sudo vim zsh && \
    sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- "--yes" && \
    usermod --shell /usr/bin/zsh user && \
    echo 'user ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/user && chmod 0440 /etc/sudoers.d/user
RUN git config --system --add safe.directory '*'
USER user

RUN uv sync --frozen --all-groups --active

COPY --chown=user:user .pre-commit-config.yaml /workspaces/dslmodel/
RUN git init && pre-commit install --install-hooks && \
    mkdir -p /opt/build/git/ && cp .git/hooks/commit-msg .git/hooks/pre-commit /opt/build/git/

ENV ANTIDOTE_VERSION=1.8.6
RUN git clone --branch v$ANTIDOTE_VERSION --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote/ && \
    echo 'zsh-users/zsh-syntax-highlighting' >> ~/.zsh_plugins.txt && \
    echo 'zsh-users/zsh-autosuggestions' >> ~/.zsh_plugins.txt && \
    echo 'source ~/.antidote/antidote.zsh' >> ~/.zshrc && \
    echo 'antidote load' >> ~/.zshrc && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    echo 'HISTFILE=~/.history/.zsh_history' >> ~/.zshrc && \
    echo 'HISTSIZE=1000' >> ~/.zshrc && \
    echo 'SAVEHIST=1000' >> ~/.zshrc && \
    echo 'setopt share_history' >> ~/.zshrc && \
    echo 'bindkey "^[[A" history-beginning-search-backward' >> ~/.zshrc && \
    echo 'bindkey "^[[B" history-beginning-search-forward' >> ~/.zshrc && \
    mkdir ~/.history/ && \
    zsh -c 'source ~/.zshrc'

# Production target: the exact dependency-closed admitted surface. It does not
# inherit the legacy builder, so historical optional integrations cannot widen
# production standing or block image construction.
FROM base AS app

RUN python -m pip install --disable-pip-version-check --no-cache-dir \
    "pydantic>=2" \
    "typer>=0.9" \
    "rich>=13.7" \
    "PyYAML>=6"

RUN mkdir -p /home/user/dslmodel
WORKDIR /home/user/dslmodel
COPY --chown=user:user src ./src
ENV PYTHONPATH=/home/user/dslmodel/src

# Build-time execution receipts: image construction fails unless the admitted
# runtime itself executes successfully under the image's Python 3.12 toolchain.
RUN python -m dslmodel.cli doctor --json --strict > /tmp/dslmodel-doctor.json && \
    python -m dslmodel.cli dsl status --json --strict > /tmp/dslmodel-status.json

ENTRYPOINT ["python", "-m", "dslmodel.cli"]
CMD ["--help"]
