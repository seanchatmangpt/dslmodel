# PyInstaller Build Guide for Autonomous Evolution System

This guide explains how to build standalone executables for the autonomous evolution system using PyInstaller and Poe tasks.

## Prerequisites

- Poetry installed and dependencies resolved
- PyInstaller installed (included in dev dependencies)
- Python 3.12+ (required for PyInstaller compatibility)

## Quick Start

### Build All Tools
```bash
poe build-all
```

### Build Individual Tools
```bash
# Build the autonomous evolution daemon
poe build-daemon

# Build the cron setup tool  
poe build-cron-setup

# Build the health check tool
poe build-health-test
```

### Create Distribution Package
```bash
poe build-package
```
This creates `dist/autonomous-evolution-tools.tar.gz` with all tools.

## Available Poe Tasks

### Main Build Tasks
- `poe build-daemon` - Build autonomous evolution daemon executable
- `poe build-cron-setup` - Build cron setup tool executable  
- `poe build-health-test` - Build health check tool executable
- `poe build-all` - Build all tools
- `poe build-package` - Create complete distribution package

### Development Tasks
- `poe build-daemon-dev` - Fast development build (unoptimized)
- `poe build-test` - Test built executables
- `poe build-clean` - Clean build artifacts

### Installation Tasks
- `poe build-install` - Install executables to system PATH
- `poe build-cross-platform` - Cross-platform build notes

## Built Executables

After building, you'll find these executables in `dist/`:

### `autonomous-evolution-daemon`
**Purpose**: Standalone autonomous evolution daemon
**Usage**: 
```bash
./autonomous-evolution-daemon start --help
./autonomous-evolution-daemon simulate --cycles 3 --fast
```

### `setup-evolution-cron`  
**Purpose**: Cron job setup and management tool
**Usage**:
```bash
./setup-evolution-cron install
./setup-evolution-cron status
./setup-evolution-cron test
```

### `autonomous-health-check`
**Purpose**: System health validation tool
**Usage**:
```bash
./autonomous-health-check  # Runs health checks
```

## Distribution Package

The `poe build-package` task creates a complete distribution with:
- All executable tools
- Configuration files (`evolution_cron.sh`)
- Proper permissions set
- Compressed tar.gz archive

## Troubleshooting

### Missing Dependencies
If you get import errors, add missing modules to the `hiddenimports` list in the spec file.

### Large Executable Size
Use development builds for testing:
```bash
poe build-daemon-dev
```

### Typer/Rich Compatibility Issues
**Fixed**: The `setup-evolution-cron` tool now uses a Typer-based implementation (`setup_evolution_cron_typer.py`) with Rich integration completely disabled to avoid PyInstaller compatibility issues.

**Error was**: `TypeError: Parameter.make_metavar() missing 1 required positional argument: 'ctx'`

**Solution**: Created a Typer version with the following settings to disable Rich:
- `pretty_exceptions_enable=False`
- `rich_markup_mode=None` 
- `os.environ["TERM"] = "dumb"`
- Using `print()` instead of Rich console methods

All Click dependencies have been removed from the codebase in favor of Typer.

### Cross-Platform Builds
PyInstaller builds for the current platform only. For other platforms:
1. Set up platform-specific environments
2. Run builds on target platforms
3. Use CI/CD for automated cross-platform builds

## Customization

### Adding New Tools
1. Create a new Poe task in `pyproject.toml`
2. Follow the pattern of existing build tasks
3. Add appropriate hidden imports and data files

### Optimizing Build Size
- Add exclusions to the spec file
- Use `--exclude-module` for unused dependencies
- Consider using `--onedir` for development builds

## Integration with Autonomous Evolution

The built executables are designed to work seamlessly with the autonomous evolution system:

1. **Daemon**: Runs continuous evolution cycles
2. **Cron Setup**: Manages scheduled execution
3. **Health Check**: Validates system state

Use these tools for production deployment where Python environments may not be available.

## Performance Notes

- Standalone executables have slower startup time
- Memory usage is higher than Python scripts
- Consider using the daemon in server environments
- Health checks are suitable for monitoring systems

## Security Considerations

- Executables include all dependencies
- No external Python installation required
- Suitable for isolated/restricted environments
- Binary verification recommended for production use