# DSL Gen Command

## Overview
The `gen` command generates DSLModel-based classes from natural language prompts using AI-powered code generation.

## Usage
```bash
# Basic usage
dsl gen "Create a user management system with authentication"

# With custom output directory
dsl gen "Generate a product catalog model" --output-dir models/

# With specific file format
dsl gen "Create API models" --file-format py

# With custom configuration
dsl gen "Generate database models" --config custom_config.yaml
```

## Options
- `--output-dir`: Directory to save generated files (default: current directory)
- `--file-format`: Output format (default: py)
- `--config`: Path to custom configuration file
- `--model`: AI model to use (default: groq/llama-3.2-90b-text-preview)

## Examples

### User Management System
```bash
dsl gen "Create a user management system with authentication, profile management, and role-based access control"
```

### API Models
```bash
dsl gen "Generate Pydantic models for a REST API with users, orders, and products"
```

### Database Models
```bash
dsl gen "Create SQLAlchemy models for an e-commerce database with relationships"
```

## Generated Output
The command generates:
- Pydantic models with validation
- Type hints and documentation
- Relationship definitions
- Optional database integration code

## Context
This command is part of the DSLModel's AI-powered code generation system, leveraging DSPy and Pydantic for robust model creation. 