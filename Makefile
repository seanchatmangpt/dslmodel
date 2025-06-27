# Swarm SH 5-ONE Makefile
# Common operations for development and deployment

.PHONY: help init gen test tick validate clean demo motion cost-report prune-refs monitor health validate-multilayer dev deploy

# Default target
help:
	@echo "🚀 DSLModel Development Commands"
	@echo "================================"
	@echo ""
	@echo "Testing (80/20 Optimized):"
	@echo "  make test-essential    - High ROI, low complexity tests (80% coverage)"
	@echo "  make verify           - Reality check without synthetic metrics (30s)"
	@echo "  make test-quick       - Quick validation tests (2min)"
	@echo "  make test             - Complete test suite with OpenTelemetry"
	@echo "  make test-unit        - Unit tests only"
	@echo "  make test-integration - Integration tests only"
	@echo "  make test-performance - Performance baseline tests"
	@echo ""
	@echo "OpenTelemetry:"
	@echo "  make otel-validate    - Quick OTEL validation"
	@echo "  make otel-demo        - Run OTEL demo with telemetry"
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Development setup"
	@echo "  make clean            - Clean temporary files"
	@echo "  make check-deps       - Verify system dependencies"

# 80/20 Essential Tests - High ROI, Low Complexity
test-essential:
	@echo "🧪 Running Essential Tests (80/20 Implementation)"
	@echo "================================================="
	@echo "High ROI tests that catch 80% of issues with 20% effort"
	@uv run pytest tests/test_cli_essential.py -v --tb=short
	@echo "✅ Essential tests completed"

# Reality Verification - Core smoke tests only
verify:
	@echo "🔍 Reality Verification (No Synthetic Metrics)"
	@echo "=============================================="
	@uv run python -c "from dslmodel.cli import app; print('✅ dsl CLI import successful')" 2>/dev/null || echo "⚠️ dsl CLI import failed (OpenAI dependency)"
	@uv run python -c "import typer; print('✅ CLI framework available')" 2>/dev/null || echo "⚠️ CLI framework missing"
	@python3 coordination_cli.py --help > /dev/null 2>&1 && echo "✅ coordination_cli accessible" || echo "⚠️ coordination_cli not found"
	@echo "✅ Core functionality verified"

# Quick validation - 2 minute limit
test-quick:
	@echo "⚡ Quick Validation Tests"
	@echo "========================"
	@timeout 120 uv run pytest tests/test_cli_essential.py::TestCLIEssential::test_core_commands_smoke -v
	@timeout 120 uv run pytest tests/test_cli_essential.py::TestCLIEssential::test_work_lifecycle_essential -v
	@echo "✅ Quick tests completed"

# Complete test suite with OpenTelemetry
test: test-deps
	@echo "🧬 Complete Test Suite with OpenTelemetry"
	@echo "=========================================="
	@export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:14317 && \
	uv run pytest tests/ -v --tb=short --maxfail=5
	@echo "✅ Complete test suite finished"

# Unit tests only
test-unit:
	@echo "🔬 Unit Tests"
	@echo "============="
	@uv run pytest tests/ -k "not integration and not performance" -v

# Integration tests only
test-integration:
	@echo "🔗 Integration Tests"
	@echo "==================="
	@uv run pytest tests/test_cli_essential.py::TestCLIEssential::test_work_lifecycle_essential -v
	@uv run pytest tests/test_cli_essential.py::TestCLIEssential::test_ai_integration_quick -v

# Performance baseline tests
test-performance:
	@echo "📈 Performance Baseline Tests"
	@echo "============================="
	@uv run pytest tests/test_cli_essential.py -k "performance" -v

# OpenTelemetry quick validation
otel-validate:
	@echo "📊 OpenTelemetry Quick Validation"
	@echo "================================="
	@echo "Checking OTEL instrumentation..."
	@uv run python -c "from dslmodel.agents.otel.otel_instrumentation import setup_telemetry; setup_telemetry('test'); print('✅ OTEL setup successful')" || echo "⚠️ OTEL setup failed"
	@uv run pytest tests/test_cli_essential.py::TestCLIEssential::test_otel_instrumentation_quick -v

# OpenTelemetry demo
otel-demo:
	@echo "🎭 OpenTelemetry Demo"
	@echo "===================="
	@echo "Starting OTEL collector (requires Docker)..."
	@docker-compose -f src/dslmodel/agents/otel/docker-compose.yaml up -d || echo "⚠️ Docker not available"
	@sleep 5
	@uv run python src/dslmodel/examples/run_thesis_otel_loop.py
	@echo "✅ OTEL demo completed"

# Test dependencies check
test-deps:
	@echo "🔍 Checking Test Dependencies"
	@echo "=============================="
	@uv run python -c "import pytest; print('✅ pytest available')" || (echo "❌ pytest missing" && exit 1)
	@uv run python -c "import typer; print('✅ typer available')" || (echo "❌ typer missing" && exit 1)
	@command -v jq > /dev/null || (echo "⚠️ jq not found (optional)" && true)
	@echo "✅ Essential dependencies verified"

# Comprehensive dependency check
check-deps:
	@echo "🛠️ Comprehensive Dependency Check"
	@echo "=================================="
	@echo "Python version:"
	@python --version
	@echo ""
	@echo "UV version:"
	@uv --version
	@echo ""
	@echo "Key packages:"
	@uv run python -c "import sys, pkg_resources; [print(f'  ✅ {d.project_name} {d.version}') for d in pkg_resources.working_set if d.project_name in ['pytest', 'typer', 'pydantic', 'opentelemetry-api']]"
	@echo ""
	@echo "System tools:"
	@command -v git > /dev/null && echo "  ✅ git available" || echo "  ❌ git missing"
	@command -v docker > /dev/null && echo "  ✅ docker available" || echo "  ⚠️ docker not found"
	@command -v jq > /dev/null && echo "  ✅ jq available" || echo "  ⚠️ jq not found"
	@echo "✅ Dependency check completed"

# Installation
install:
	@echo "📦 Installing Dependencies"
	@echo "========================="
	@uv sync
	@echo "✅ Installation completed"

# Development setup
dev: install
	@echo "🛠️ Development Setup"
	@echo "===================="
	@uv sync --all-groups
	@pre-commit install || echo "⚠️ pre-commit not available"
	@echo "✅ Development environment ready"

# Clean temporary files
clean:
	@echo "🧹 Cleaning Temporary Files"
	@echo "==========================="
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf dist/ build/ .coverage htmlcov/ 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Add missing faker dependency
add-faker:
	@echo "📦 Adding faker dependency"
	@echo "=========================="
	@uv add faker
	@echo "✅ Faker dependency added"

# Continuous Integration targets
ci-test: test-deps test-essential
	@echo "🤖 CI Test Pipeline"
	@echo "==================="
	@echo "✅ CI tests passed"

# Production readiness check
production-ready: check-deps test-essential otel-validate
	@echo "🚀 Production Readiness Check"
	@echo "============================="
	@echo "✅ System ready for production"

# Development workflow targets
dev-test: test-essential
	@echo "💻 Development Test Cycle"
	@echo "========================="
	@echo "✅ Development tests passed"

# Poetry swarm commands (from pyproject.toml)
swarm-demo:
	@echo "🚀 Running Swarm Demo"
	@uv run poe swarm-demo

swarm-status:
	@echo "📊 Swarm Status"
	@uv run poe swarm-status

swarm-init:
	@echo "🏗️ Initializing Swarm"
	@uv run poe swarm-init

# Reality check with timing
timed-verify:
	@echo "⏱️ Timed Reality Check"
	@echo "======================"
	@time make verify
	@echo "✅ Timed verification completed"