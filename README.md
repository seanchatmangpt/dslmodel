# DSLModel - Telemetry-driven Development Platform

## Installation

### Using UV (Recommended)
```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/seanchatmangpt/dslmodel.git
cd dslmodel
uv sync --extra otel  # Install with OpenTelemetry support
```

### Using pip
```bash
pip install dslmodel[otel]
```

## Quick Start
```python
from dslmodel import generate_and_save_dslmodel

# Generate a model from natural language
model_class, output_file = generate_and_save_dslmodel(
    "Create a User model with name, email, and age fields"
)
```

### CLI Usage
```bash
# Generate a model
uv run dsl gen "Create a Task model with title, description, and status"

# Run health checks
uv run dsl health-8020 analyze

# View available commands
uv run dsl --help
```

## Development

### Setup Development Environment
```bash
# Install all dependencies including dev tools
uv sync --all-groups

# Run tests
uv run pytest

# Run specific test suites
uv run make test-essential  # 80/20 essential tests
uv run make test-quick      # Quick validation
```

## Features
- 🧬 **DSPy Integration**: Natural language to Pydantic model generation
- 📊 **OpenTelemetry**: Built-in observability and tracing
- 🤖 **SwarmAgent**: Multi-agent coordination system
- 🎯 **80/20 Principle**: Focus on high-impact features
- 🔄 **Evolution Engine**: Continuous improvement system

## Migration from Poetry

This project has migrated from Poetry to UV for faster dependency management.
If you have an existing Poetry installation:

```bash
# Remove poetry.lock (already done)
rm poetry.lock

# Sync with UV
uv sync
```

## Documentation

See the `context/` directory for comprehensive documentation:
- `context/index.md` - Project overview and architecture
- `context/docs.md` - Technical documentation
- `context/otel.md` - OpenTelemetry integration

## License

MIT
