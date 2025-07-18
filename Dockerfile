# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12
FROM python:$PYTHON_VERSION-slim AS base

# Remove docker-clean so we can keep the apt cache in Docker build cache.
RUN rm /etc/apt/apt.conf.d/docker-clean

# Create a non-root user and switch to it [1].
# [1] https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG UID=1000
ARG GID=$UID
RUN groupadd --gid $GID user && \
    useradd --create-home --gid $GID --uid $UID user --no-log-init && \
    chown user /opt/
USER user

# Create and activate a virtual environments.
ENV VIRTUAL_ENV /opt/dslmodel-env
ENV PATH $VIRTUAL_ENV/bin:$PATH
RUN python -m venv $VIRTUAL_ENV

# Set the working directory.
WORKDIR /workspaces/dslmodel/

FROM base as builder

USER root

# Install uv
RUN --mount=type=cache,target=/root/.cache/pip/ \
    curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install compilers that may be required for certain packages or platforms.
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes build-essential

USER user

# Install the run time Python dependencies in the virtual environments.
COPY --chown=user:user pyproject.toml uv.lock uv.toml /workspaces/dslmodel/
RUN mkdir -p src/dslmodel/ && touch src/dslmodel/__init__.py && touch README.md
RUN uv sync --frozen

FROM builder as dev

# Install development tools: curl, git, gpg, ssh, starship, sudo, vim, and zsh.
USER root
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes curl git gnupg ssh sudo vim zsh && \
    sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- "--yes" && \
    usermod --shell /usr/bin/zsh user && \
    echo 'user ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/user && chmod 0440 /etc/sudoers.d/user
RUN git config --system --add safe.directory '*'
USER user

# Install the development Python dependencies in the virtual environments.
RUN uv sync --frozen --all-groups

# Persist output generated during docker build so that we can restore it in the dev container.
COPY --chown=user:user .pre-commit-config.yaml /workspaces/dslmodel/
RUN git init && pre-commit install --install-hooks && \
    mkdir -p /opt/build/git/ && cp .git/hooks/commit-msg .git/hooks/pre-commit /opt/build/git/

# Configure the non-root user's shell.
ENV ANTIDOTE_VERSION 1.8.6
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

FROM base AS app

# Copy the virtual environments from the builder stage.
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV

# Copy the app source code to the working directory.
COPY --chown=user:user . .

# Expose the app.
ENTRYPOINT ["/opt/dslmodel-env/bin/dslmodel"]
CMD []
