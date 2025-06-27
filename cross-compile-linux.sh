#!/bin/bash
# Script to build Linux executable using Docker

set -e

echo "🐧 Building Linux executable using Docker..."

# Create a Dockerfile for building
cat > Dockerfile.build-linux << 'EOF'
FROM python:3.12-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and PyInstaller
RUN pip install poetry pyinstaller

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY setup_evolution_cron_typer.py ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Build the executable
RUN pyinstaller --onefile \
    --name=setup-evolution-cron-linux \
    --hidden-import=typer \
    --hidden-import=typer.core \
    --hidden-import=typer.main \
    setup_evolution_cron_typer.py

# Create output stage
FROM scratch AS output
COPY --from=0 /app/dist/setup-evolution-cron-linux /
EOF

# Build and extract the Linux executable
echo "Building Linux executable..."
DOCKER_BUILDKIT=1 docker build -f Dockerfile.build-linux --output type=local,dest=./dist/linux . || {
    echo "❌ Docker build failed. Trying alternative approach..."
    
    # Alternative: Use buildx for cross-platform
    docker buildx create --use --name multibuilder || true
    docker buildx build --platform linux/amd64 -f Dockerfile.build-linux --output type=local,dest=./dist/linux .
}

# Check if build succeeded
if [ -f "dist/linux/setup-evolution-cron-linux" ]; then
    echo "✅ Linux executable built successfully!"
    ls -lh dist/linux/
    file dist/linux/setup-evolution-cron-linux
else
    echo "❌ Build failed"
    exit 1
fi

# Cleanup
rm -f Dockerfile.build-linux

echo ""
echo "📦 Linux executable available at: dist/linux/setup-evolution-cron-linux"