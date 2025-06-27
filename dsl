#!/usr/bin/env bash
# DSLModel UV Wrapper - Simplifies UV commands
# This wrapper makes it easy to run DSL commands without typing "uv run" every time

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# If no arguments, show help
if [ $# -eq 0 ]; then
    uv run dsl --help
    exit 0
fi

# Special commands that don't use the dsl CLI
case "$1" in
    "install")
        echo "📦 Installing DSLModel with UV..."
        uv sync --extra otel
        ;;
    "install-dev")
        echo "📦 Installing DSLModel with all dev dependencies..."
        uv sync --all-groups
        ;;
    "test")
        echo "🧪 Running tests..."
        uv run pytest "${@:2}"
        ;;
    "test-essential")
        echo "🧪 Running essential tests (80/20)..."
        uv run make test-essential
        ;;
    "test-quick")
        echo "⚡ Running quick tests..."
        uv run make test-quick
        ;;
    "make")
        # Pass through to make
        uv run make "${@:2}"
        ;;
    "add")
        # Add a dependency
        echo "➕ Adding dependency..."
        uv add "${@:2}"
        ;;
    "add-dev")
        # Add a dev dependency
        echo "➕ Adding dev dependency..."
        uv add --dev "${@:2}"
        ;;
    "update")
        echo "🔄 Updating dependencies..."
        uv lock --upgrade
        ;;
    "shell")
        echo "🐚 Entering UV shell..."
        uv run bash
        ;;
    "python")
        # Direct python access
        uv run python "${@:2}"
        ;;
    "poe")
        # Run poethepoet tasks
        uv run poe "${@:2}"
        ;;
    *)
        # Default: pass all arguments to dsl CLI
        uv run dsl "$@"
        ;;
esac